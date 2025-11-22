"""Automated test runner for pop gen command."""
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


class TestCase:
    """Represents a single test case."""

    def __init__(self, name: str, input_query: str, expected_output: str):
        self.name = name
        self.input_query = input_query
        self.expected_output = expected_output
        self.actual_output: str = ""
        self.passed: bool = False
        self.error: str = ""

    def normalize_command(self, command: str) -> str:
        """Normalize command for comparison."""
        # Remove extra whitespace
        command = " ".join(command.split())
        # Remove leading/trailing whitespace
        command = command.strip()
        return command

    def check_result(self) -> bool:
        """Check if actual output matches expected."""
        normalized_actual = self.normalize_command(self.actual_output)
        normalized_expected = self.normalize_command(self.expected_output)

        # Direct match
        if normalized_actual == normalized_expected:
            self.passed = True
            return True

        # Check if expected is a substring of actual
        if normalized_expected in normalized_actual:
            self.passed = True
            return True

        # Check if actual contains key parts of expected
        expected_parts = normalized_expected.split()
        actual_parts = normalized_actual.split()

        # Check if main command matches
        if expected_parts and actual_parts:
            if expected_parts[0] == actual_parts[0]:
                # Main command matches, check if it's close enough
                if len(set(expected_parts) & set(actual_parts)) >= len(expected_parts) * 0.7:
                    self.passed = True
                    return True

        return False


def load_test_cases() -> List[TestCase]:
    """Load test cases from TEST_CASES.md."""
    test_cases = []
    test_file = Path(__file__).parent.parent / "docs" / "TEST_CASES.md"

    if not test_file.exists():
        console.print(f"[red]Error:[/red] Test cases file not found: {test_file}")
        return test_cases

    content = test_file.read_text(encoding="utf-8")
    
    # Parse test cases using regex
    # Pattern: ## Test Case N: Title\n**Input**: "query"\n**Expected**: `command`
    pattern = r"## Test Case (\d+):\s*([^\n]+)\n\*\*Input\*\*:\s*\"([^\"]+)\"\n\*\*Expected\*\*:\s*`([^`]+)`"
    matches = re.findall(pattern, content, re.MULTILINE)

    for match in matches:
        case_num, title, input_query, expected = match
        test_case = TestCase(
            name=f"Test Case {case_num}: {title.strip()}",
            input_query=input_query.strip(),
            expected_output=expected.strip(),
        )
        test_cases.append(test_case)

    # Also try alternative format (with "or" in expected)
    if not test_cases:
        # Fallback: simpler pattern
        pattern2 = r"## Test Case (\d+):\s*([^\n]+)\n\*\*Input\*\*:\s*\"([^\"]+)\"\n\*\*Expected\*\*:\s*`([^`]+)`"
        matches2 = re.findall(pattern2, content, re.MULTILINE | re.DOTALL)
        
        for match in matches2:
            case_num, title, input_query, expected = match
            # Handle "or" in expected - take first option
            expected = expected.split(" or ")[0].strip()
            test_case = TestCase(
                name=f"Test Case {case_num}: {title.strip()}",
                input_query=input_query.strip(),
                expected_output=expected.strip(),
            )
            test_cases.append(test_case)

    return test_cases


def run_test_case(test_case: TestCase, timeout: int = 60) -> Tuple[bool, str]:
    """
    Run a single test case.

    Returns:
        Tuple of (success, output)
    """
    try:
        # Ensure PATH includes .local/bin
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"

        # Run pop gen command
        cmd = ["pop", "gen", test_case.input_query]

        # Use subprocess to run and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            stdin=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
        )

        # Send 'A' (Abort) to skip execution prompt, with timeout
        try:
            stdout, _ = process.communicate(input="A\n", timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return False, "Timeout"

        output = stdout

        # Extract command from output using multiple strategies
        extracted_command = ""

        # Strategy 1: Look for Panel content (between │ markers)
        panel_pattern = r"│\s+([^\n│]+?)\s+│"
        panel_matches = re.findall(panel_pattern, output)
        if panel_matches:
            # Filter out UI elements and take the longest command-like string
            for match in panel_matches:
                match = match.strip()
                # Skip if it's just UI decoration or too short
                if len(match) > 3 and not match.startswith(("─", "╭", "╰")):
                    if not extracted_command or len(match) > len(extracted_command):
                        extracted_command = match

        # Strategy 2: Look for common command patterns
        if not extracted_command:
            command_patterns = [
                r"(ls\s+-[lah]+)",
                r"(find\s+[^\n]+)",
                r"(git\s+[^\n]+)",
                r"(ps\s+[^\n]+)",
                r"(curl\s+[^\n]+)",
                r"(export\s+[^\n]+)",
                r"(du\s+[^\n]+)",
                r"(vm_stat\s*[^\n]*)",
                r"(df\s+-[h]+)",
                r"(#\s*WARNING[^\n]*)",
            ]
            
            for pattern in command_patterns:
                matches = re.findall(pattern, output, re.MULTILINE)
                if matches:
                    # Take the longest match
                    extracted_command = max(matches, key=len).strip()
                    break

        # Strategy 3: Extract from lines that look like commands
        if not extracted_command:
            lines = output.split("\n")
            for line in lines:
                line = line.strip()
                # Skip UI elements and empty lines
                if not line or line.startswith(("╭", "╰", "│", "─", "Thinking", "Generated", "Executing")):
                    continue
                # Check if line looks like a command (starts with letter, not too long)
                if re.match(r"^[#a-zA-Z][a-zA-Z0-9_\-./$:&|<> ]+$", line):
                    if 3 < len(line) < 200:
                        extracted_command = line
                        break

        # Strategy 4: Look for any line after "Generated Command" that's not UI
        if not extracted_command:
            found_panel = False
            lines = output.split("\n")
            for line in lines:
                if "Generated Command" in line:
                    found_panel = True
                    continue
                if found_panel:
                    line = line.strip()
                    # Skip UI elements
                    if line and not line.startswith(("╭", "╰", "│", "─", "[E]xecute")):
                        # Remove │ markers if present
                        line = re.sub(r"^│\s*|\s*│$", "", line).strip()
                        if line and len(line) > 3:
                            extracted_command = line
                            break

        test_case.actual_output = extracted_command
        return True, extracted_command

    except Exception as e:
        return False, f"Error: {str(e)}"


def run_all_tests(verbose: bool = False) -> Dict[str, any]:
    """Run all test cases and return results."""
    test_cases = load_test_cases()

    if not test_cases:
        console.print("[red]No test cases found![/red]")
        return {"total": 0, "passed": 0, "failed": 0, "cases": []}

    console.print(f"\n[bold blue]Running {len(test_cases)} test cases...[/bold blue]\n")

    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "cases": [],
    }

    for i, test_case in enumerate(test_cases, 1):
        console.print(f"[dim]Running {test_case.name}...[/dim]", end=" ")

        success, output = run_test_case(test_case)

        if success:
            test_case.passed = test_case.check_result()
            if test_case.passed:
                results["passed"] += 1
                console.print("[green]✓ PASS[/green]")
            else:
                results["failed"] += 1
                console.print("[red]✗ FAIL[/red]")
                if verbose:
                    console.print(f"  Expected: {test_case.expected_output}")
                    console.print(f"  Got: {test_case.actual_output}")
        else:
            results["failed"] += 1
            test_case.error = output
            console.print(f"[red]✗ ERROR: {output}[/red]")

        results["cases"].append(test_case)

    return results


def print_results(results: Dict[str, any], verbose: bool = False):
    """Print test results in a formatted table."""
    console.print("\n" + "=" * 60)
    console.print("[bold]Test Results[/bold]")
    console.print("=" * 60 + "\n")

    # Summary
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    summary_text = f"""
Total Tests: {total}
Passed: [green]{passed}[/green]
Failed: [red]{failed}[/red]
Pass Rate: [bold]{pass_rate:.1f}%[/bold]
    """

    console.print(Panel(summary_text.strip(), title="Summary", border_style="blue"))

    # Detailed results table
    if verbose or failed > 0:
        table = Table(title="Detailed Results")
        table.add_column("Test Case", style="cyan")
        table.add_column("Input", style="yellow", max_width=30)
        table.add_column("Expected", style="green", max_width=30)
        table.add_column("Actual", style="magenta", max_width=30)
        table.add_column("Status", style="bold")

        for case in results["cases"]:
            status = "[green]✓ PASS[/green]" if case.passed else "[red]✗ FAIL[/red]"
            if case.error:
                status = f"[red]ERROR: {case.error}[/red]"

            table.add_row(
                case.name,
                case.input_query[:30] + "..." if len(case.input_query) > 30 else case.input_query,
                case.expected_output[:30] + "..." if len(case.expected_output) > 30 else case.expected_output,
                case.actual_output[:30] + "..." if len(case.actual_output) > 30 else case.actual_output,
                status,
            )

        console.print("\n")
        console.print(table)

    # Exit code
    return 0 if failed == 0 else 1


def main(verbose: bool = False):
    """Main test runner."""
    console.print("[bold blue]Parallax OpsPilot - Automated Test Runner[/bold blue]\n")

    # Check if pop command is available
    env = os.environ.copy()
    env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
    
    try:
        result = subprocess.run(
            ["pop", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
            env=env,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[red]Error:[/red] 'pop' command not found. Please install the project first.")
        console.print("Run: pip install -e .")
        return 1

    results = run_all_tests(verbose=verbose)
    return print_results(results, verbose=verbose)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated tests for Parallax OpsPilot")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed results",
    )
    args = parser.parse_args()

    exit_code = main(verbose=args.verbose)
    sys.exit(exit_code)

