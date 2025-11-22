"""Tests for utility functions."""
import os
import platform
from unittest.mock import patch

import pytest

from src.utils import get_system_info


class TestGetSystemInfo:
    """Test get_system_info function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        result = get_system_info()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_os_info(self):
        """Test that result contains OS information."""
        result = get_system_info()
        system = platform.system()

        if system == "Darwin":
            assert "macOS" in result or "Darwin" in result
        elif system == "Linux":
            assert "Linux" in result
        elif system == "Windows":
            assert "Windows" in result

    def test_contains_shell_info(self):
        """Test that result contains shell information."""
        result = get_system_info()
        # Should contain a path-like string (shell path)
        assert "/" in result or "\\" in result

    @patch.dict(os.environ, {"SHELL": "/bin/zsh"})
    def test_uses_shell_env_var(self):
        """Test that function uses SHELL environment variable."""
        result = get_system_info()
        assert "/bin/zsh" in result

    @patch.dict(os.environ, {}, clear=True)
    def test_fallback_shell(self):
        """Test fallback shell when SHELL is not set."""
        result = get_system_info()
        # Should still return a valid shell path
        assert "/" in result or "\\" in result

    @patch("platform.system", return_value="Darwin")
    def test_macos_detection(self, mock_system):
        """Test macOS detection."""
        result = get_system_info()
        assert "macOS" in result

    @patch("platform.system", return_value="Linux")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("builtins.open", create=True)
    def test_linux_detection(self, mock_open, mock_exists, mock_system):
        """Test Linux detection with os-release."""
        mock_open.return_value.__enter__.return_value = iter(
            ['PRETTY_NAME="Ubuntu 22.04"\n']
        )
        result = get_system_info()
        assert "Linux" in result or "Ubuntu" in result

