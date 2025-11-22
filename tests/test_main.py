"""Tests for main CLI module."""
import re
from unittest.mock import MagicMock, patch

import pytest
import typer.testing

from src.main import _strip_markdown_code_blocks, app


class TestStripMarkdownCodeBlocks:
    """Test markdown code block stripping function."""

    def test_removes_simple_code_blocks(self):
        """Test removal of simple code blocks."""
        text = "```bash\nls -la\n```"
        result = _strip_markdown_code_blocks(text)
        assert "```" not in result
        assert "ls -la" in result

    def test_removes_code_blocks_with_language(self):
        """Test removal of code blocks with language tag."""
        text = "```bash\nfind . -name '*.py'\n```"
        result = _strip_markdown_code_blocks(text)
        assert "```" not in result
        assert "find" in result

    def test_handles_multiline_commands(self):
        """Test handling of multiline commands."""
        text = "```\ngit status\ngit log -3\n```"
        result = _strip_markdown_code_blocks(text)
        assert "git status" in result
        assert "git log" in result

    def test_handles_text_without_code_blocks(self):
        """Test handling of text without code blocks."""
        text = "ls -la"
        result = _strip_markdown_code_blocks(text)
        assert result == "ls -la"

    def test_removes_reasoning_tags(self):
        """Test removal of reasoning tags."""
        text = "<think>Some reasoning</think>\nls -la"
        result = _strip_markdown_code_blocks(text)
        assert "<think>" not in result
        assert "ls -la" in result

    def test_extracts_command_from_mixed_content(self):
        """Test extraction of command from mixed content."""
        text = "Okay, the user wants to list files.\nls -la\nThat should work."
        result = _strip_markdown_code_blocks(text)
        # Should extract the actual command
        assert "ls -la" in result


class TestCLICommands:
    """Test CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Typer test runner."""
        return typer.testing.CliRunner()

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Parallax OpsPilot" in result.stdout

    def test_configure_command_help(self, runner):
        """Test configure command help."""
        result = runner.invoke(app, ["configure", "--help"])
        assert result.exit_code == 0
        assert "configure" in result.stdout.lower()

    @patch("src.main.config_manager")
    @patch("src.main.typer.prompt")
    def test_configure_command(self, mock_prompt, mock_config_manager, runner):
        """Test configure command."""
        # Mock prompts
        mock_prompt.side_effect = [
            "http://localhost:3000/v1",  # api_base
            "Qwen/Qwen3-0.6B",  # model
        ]

        # Mock config manager
        mock_config = MagicMock()
        mock_config.api_base = "http://localhost:8000/v1"
        mock_config.api_key = "parallax"
        mock_config.model = "gradient/Llama-3-8B-Instruct"
        mock_config_manager.get.return_value = mock_config

        result = runner.invoke(app, ["configure"])

        # Should call save
        assert mock_config_manager.save.called

    @patch("src.main.ParallaxClient")
    @patch("src.main.get_system_info")
    @patch("src.main.config_manager")
    def test_gen_command_mock(self, mock_config, mock_system, mock_client_class, runner):
        """Test gen command with mocked dependencies."""
        # Setup mocks
        mock_config_obj = MagicMock()
        mock_config_obj.api_base = "http://localhost:3000/v1"
        mock_config_obj.api_key = "test"
        mock_config_obj.model = "test-model"
        mock_config.get.return_value = mock_config_obj

        mock_system.return_value = "macOS /bin/zsh"

        mock_client = MagicMock()
        mock_client.generate_command_stream.return_value = iter(["ls", " -la"])
        mock_client_class.return_value = mock_client

        # Run command (will need to handle interactive prompts)
        # This is a simplified test - full integration test would be more complex
        result = runner.invoke(app, ["gen", "list files"], input="A\n")

        # Verify client was created
        mock_client_class.assert_called_once()

