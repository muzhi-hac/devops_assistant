"""Tests for configuration management."""
import tempfile
from pathlib import Path

import pytest
import yaml

from src.config import AppConfig, ConfigManager


class TestAppConfig:
    """Test AppConfig model."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AppConfig()
        assert config.api_base == "http://localhost:8000/v1"
        assert config.api_key == "parallax"
        assert config.model == "gradient/Llama-3-8B-Instruct"

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AppConfig(
            api_base="http://localhost:3000/v1",
            api_key="test-key",
            model="Qwen/Qwen3-0.6B",
        )
        assert config.api_base == "http://localhost:3000/v1"
        assert config.api_key == "test-key"
        assert config.model == "Qwen/Qwen3-0.6B"

    def test_api_base_validation(self):
        """Test API base URL validation."""
        # Valid URLs
        config1 = AppConfig(api_base="http://localhost:3000/v1")
        assert config1.api_base == "http://localhost:3000/v1"

        config2 = AppConfig(api_base="https://api.example.com/v1")
        assert config2.api_base == "https://api.example.com/v1"

        # Invalid URLs
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            AppConfig(api_base="localhost:3000/v1")

        with pytest.raises(ValueError, match="must end with /v1"):
            AppConfig(api_base="http://localhost:3000")


class TestConfigManager:
    """Test ConfigManager class."""

    def test_load_default_config(self):
        """Test loading default configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=config_path)

            config = manager.load()
            assert isinstance(config, AppConfig)
            assert config.api_base == "http://localhost:8000/v1"
            assert config_path.exists()  # Should create default config

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=config_path)

            # Save custom config
            custom_config = AppConfig(
                api_base="http://localhost:3000/v1",
                api_key="test-key",
                model="Qwen/Qwen3-0.6B",
            )
            manager.save(custom_config)

            # Load and verify
            loaded_config = manager.load()
            assert loaded_config.api_base == "http://localhost:3000/v1"
            assert loaded_config.api_key == "test-key"
            assert loaded_config.model == "Qwen/Qwen3-0.6B"

    def test_update_config(self):
        """Test updating configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            manager = ConfigManager(config_path=config_path)

            # Load default
            config = manager.load()

            # Update
            updated = manager.update(api_base="http://localhost:3000/v1", model="test-model")

            assert updated.api_base == "http://localhost:3000/v1"
            assert updated.model == "test-model"
            assert updated.api_key == config.api_key  # Should preserve other values

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("invalid: yaml: content: [unclosed")

            manager = ConfigManager(config_path=config_path)

            with pytest.raises(ValueError, match="Invalid configuration file"):
                manager.load()

