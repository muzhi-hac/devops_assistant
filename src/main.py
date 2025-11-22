"""Main entry point for Parallax OpsPilot CLI."""
import re
import subprocess
from typing import Annotated

import pyperclip
import typer
from rich.console import Console
from rich.panel import Panel

from .client import ParallaxClient, ParallaxConnectionError
from .config import AppConfig, ConfigManager
from .utils import get_system_info

# Initialize Typer app and Rich console
app = typer.Typer(
    name="pop",
    help="Parallax OpsPilot - Terminal-based AI copilot for DevOps engineers",
)
console = Console()

# Global config manager instance
config_manager = ConfigManager()


def version_callback(value: bool) -> None:
    """Handle --version flag."""
    if value:
        console.print("[bold blue]Parallax OpsPilot[/bold blue] v0.1.0")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
    ),
) -> None:
    """Parallax OpsPilot - Terminal-based AI copilot for DevOps engineers."""
    pass


@app.command()
def configure() -> None:
    """
    Configure Parallax OpsPilot settings interactively.

    Prompts the user for API base URL and model name, showing current values as defaults.
    """
    # Load current configuration
    current_config = config_manager.get()

    # Prompt for api_base with current value as default
    api_base = typer.prompt(
        "API Base URL",
        default=current_config.api_base,
        type=str,
    )

    # Prompt for model_name with current value as default
    # Note: Using 'model' field from config, but prompt shows as 'model_name'
    model_name = typer.prompt(
        "Model Name",
        default=current_config.model,
        type=str,
    )

    # Create updated configuration
    try:
        updated_config = AppConfig(
            api_base=api_base,
            api_key=current_config.api_key,  # Keep existing API key
            model=model_name,
        )
        config_manager.save(updated_config)

        # Print success message with checkmark emoji
        console.print("\n[bold green]✓[/bold green] Configuration saved successfully!")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def _strip_markdown_code_blocks(text: str) -> str:
    """
    Clean and extract the actual command from LLM output.

    Removes markdown code blocks, reasoning tags, and extracts the command.

    Args:
        text: Raw text from LLM that may contain markdown, reasoning, etc.

    Returns:
        Clean command string.
    """
    # Remove <think>...</think> tags and their content (multiple patterns)
    # Handle both <think> and <think> tags
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove ```bash, ```sh, ```shell, or just ```
    text = re.sub(r"^```(?:bash|sh|shell)?\s*\n?", "", text, flags=re.MULTILINE)
    # Remove closing ```
    text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
    
    # Split by lines and find the actual command
    lines = text.split("\n")
    command_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip lines that look like reasoning/explanation (contain common explanation words)
        if re.search(r"^(okay|wait|first|i need|let me|the user|since|but|maybe|so|that|i should|let me check)", line, re.IGNORECASE):
            continue
        # Skip lines that are clearly explanations (too long, contain punctuation like periods)
        if len(line) > 80 and ("." in line or "?" in line or "!" in line):
            continue
        # Skip lines containing reasoning keywords
        if re.search(r"\b(need to|should|might|would|could|think|consider|check|wait|since|but|maybe)\b", line, re.IGNORECASE):
            if len(line) > 50:  # Only skip if it's a longer explanation
                continue
        # This looks like a command
        command_lines.append(line)
    
    # If we found command lines, join them
    if command_lines:
        result = "\n".join(command_lines)
    else:
        # Fallback: just clean the original text
        result = text
    
    # Final cleanup: remove any remaining markdown or extra whitespace
    result = re.sub(r"^```.*?```$", "", result, flags=re.DOTALL | re.MULTILINE)
    result = result.strip()
    
    # If result is still too long or contains explanation-like text, try to extract just the command part
    # Look for lines that start with common command patterns
    lines = result.split("\n")
    for line in lines:
        line = line.strip()
        # Skip empty or very short lines
        if not line or len(line) < 2:
            continue
        # Check if this line looks like a shell command (starts with common commands or #)
        if re.match(r"^(#|ls|cd|mkdir|rm|cp|mv|grep|find|cat|echo|curl|wget|git|docker|kubectl|python|node|npm|yarn|sudo|brew|apt|yum|pip|conda|export|alias)", line, re.IGNORECASE):
            return line
        # Also check if line contains common shell operators but doesn't look like explanation
        if re.search(r"^[a-zA-Z][a-zA-Z0-9_-]*\s+", line) and not re.search(r"\.(txt|log|json|yaml|yml)$", line):
            # Looks like a command with arguments
            if len(line) < 200:  # Not too long
                return line
    
    return result


@app.command()
def gen(
    query: Annotated[str, typer.Argument(help="Natural language query for command generation")],
) -> None:
    """
    Generate shell commands from natural language queries.

    This command will:
    1. Detect OS/Shell
    2. Send prompt to Parallax
    3. Stream response
    4. Parse and extract code blocks
    5. Prompt user for action (Execute/Copy/Abort)

    Args:
        query: Natural language description of the desired command.
    """
    # Load config and initialize client
    try:
        config = config_manager.get()
        client = ParallaxClient(config)
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    # Get system info
    system_info = get_system_info()

    # Stream the response
    accumulated_command = ""
    first_chunk = True
    in_reasoning_tag = False
    reasoning_buffer = ""

    try:
        with console.status("[bold yellow]Thinking...", spinner="dots"):
            for chunk in client.generate_command_stream(query, system_info):
                accumulated_command += chunk
                
                # Check if we're entering a reasoning tag
                chunk_lower = chunk.lower()
                if "<think>" in chunk_lower or "<think>" in chunk_lower:
                    in_reasoning_tag = True
                    reasoning_buffer = ""
                    continue
                
                # Check if we're exiting a reasoning tag
                if in_reasoning_tag:
                    reasoning_buffer += chunk
                    if "</think>" in chunk_lower or "</think>" in chunk_lower or "</think>" in chunk_lower:
                        in_reasoning_tag = False
                        reasoning_buffer = ""
                    continue
                
                # Only print chunks that are not in reasoning tags
                if not in_reasoning_tag:
                    if first_chunk:
                        # Clear the status spinner and start printing
                        console.print()  # New line after spinner
                        first_chunk = False
                    
                    # Print chunk in real-time with yellow color
                    console.print(chunk, style="yellow", end="")

        console.print()  # New line after streaming

    except ParallaxConnectionError as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e.message}")
        raise typer.Exit(code=1)

    if not accumulated_command:
        console.print("[bold red]No command generated.[/bold red]")
        raise typer.Exit(code=1)

    # Post-processing: strip markdown code blocks
    clean_command = _strip_markdown_code_blocks(accumulated_command)

    if not clean_command:
        console.print("[bold red]Generated command is empty after processing.[/bold red]")
        raise typer.Exit(code=1)

    # Show the final clean command in a panel
    console.print()
    console.print(
        Panel(
            clean_command,
            title="[bold green]Generated Command[/bold green]",
            border_style="green",
        )
    )

    # User interaction
    console.print()
    action = typer.prompt(
        "[E]xecute, [C]opy, [A]bort?",
        default="A",
        type=str,
    ).upper()

    if action == "E":
        # Execute the command
        console.print("\n[bold yellow]Executing command...[/bold yellow]\n")
        try:
            result = subprocess.run(
                clean_command,
                shell=True,
                check=False,  # Don't raise on non-zero exit
            )
            console.print(f"\n[bold]Exit code:[/bold] {result.returncode}")
        except Exception as e:
            console.print(f"[bold red]Error executing command:[/bold red] {e}")
            raise typer.Exit(code=1)
    elif action == "C":
        # Copy to clipboard
        try:
            pyperclip.copy(clean_command)
            console.print("[bold green]✓ Command copied to clipboard![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error copying to clipboard:[/bold red] {e}")
            console.print(f"[dim]Command: {clean_command}[/dim]")
    elif action == "A":
        console.print("[dim]Aborted.[/dim]")
    else:
        console.print(f"[bold red]Invalid choice: {action}[/bold red]")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
