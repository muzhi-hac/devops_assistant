"""Tests for Parallax client."""
from unittest.mock import MagicMock, patch

import pytest
from openai import APIConnectionError

from src.client import ParallaxConnectionError, ParallaxClient
from src.config import AppConfig


class TestParallaxClient:
    """Test ParallaxClient class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return AppConfig(
            api_base="http://localhost:3000/v1",
            api_key="test-key",
            model="test-model",
        )

    @pytest.fixture
    def client(self, config):
        """Create a test client."""
        return ParallaxClient(config)

    def test_client_initialization(self, config):
        """Test client initialization."""
        client = ParallaxClient(config)
        assert client.config == config
        assert client.client is not None

    @patch("src.client.OpenAI")
    def test_client_base_url(self, mock_openai, config):
        """Test that client uses correct base URL."""
        ParallaxClient(config)
        mock_openai.assert_called_once_with(
            base_url=config.api_base,
            api_key=config.api_key,
        )

    @patch("src.client.OpenAI")
    def test_generate_command_stream_success(self, mock_openai, config):
        """Test successful command generation."""
        # Mock stream response
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "ls -la"

        mock_stream = [mock_chunk]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_stream
        mock_openai.return_value = mock_client

        client = ParallaxClient(config)
        result = list(client.generate_command_stream("list files", "macOS /bin/zsh"))

        assert len(result) > 0
        assert "ls" in result[0]

    @patch("src.client.OpenAI")
    def test_generate_command_stream_connection_error(self, mock_openai, config):
        """Test handling of connection errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIConnectionError(
            "Connection failed"
        )
        mock_openai.return_value = mock_client

        client = ParallaxClient(config)

        with pytest.raises(ParallaxConnectionError) as exc_info:
            list(client.generate_command_stream("test", "macOS /bin/zsh"))

        assert "Failed to connect" in str(exc_info.value)
        assert "Is Parallax running" in str(exc_info.value)

    def test_generate_command_stream_includes_system_info(self, client):
        """Test that system info is included in user message."""
        with patch.object(client.client.chat.completions, "create") as mock_create:
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta.content = "test"
            mock_create.return_value = [mock_chunk]

            list(client.generate_command_stream("test query", "macOS /bin/zsh"))

            # Verify the call was made with correct messages
            call_args = mock_create.call_args
            messages = call_args.kwargs["messages"]

            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert "macOS /bin/zsh" in messages[1]["content"]
            assert "test query" in messages[1]["content"]

    def test_generate_command_stream_uses_correct_model(self, client):
        """Test that correct model is used."""
        with patch.object(client.client.chat.completions, "create") as mock_create:
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta.content = "test"
            mock_create.return_value = [mock_chunk]

            list(client.generate_command_stream("test", "macOS /bin/zsh"))

            call_args = mock_create.call_args
            assert call_args.kwargs["model"] == client.config.model
            assert call_args.kwargs["stream"] is True
            assert call_args.kwargs["temperature"] == 0.1

