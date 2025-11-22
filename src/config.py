"""Configuration management for Parallax OpsPilot."""
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class AppConfig(BaseModel):
    """Application configuration model."""

    api_base: str = Field(
        default="http://localhost:8000/v1",
        description="Base URL for the Parallax inference server",
    )
    api_key: str = Field(
        default="parallax",
        description="API key for authentication",
    )
    model: str = Field(
        default="gradient/Llama-3-8B-Instruct",
        description="Model name to use for inference",
    )

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """Validate API base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("api_base must start with http:// or https://")
        if not v.endswith("/v1"):
            raise ValueError("api_base must end with /v1")
        return v


class ConfigManager:
    """Manages configuration loading and saving."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file. If None, uses default location.
        """
        if config_path is None:
            # Default to ~/.config/pop/config.yaml on Unix-like systems
            home = Path.home()
            config_dir = home / ".config" / "pop"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.yaml"
        else:
            self.config_path = config_path

        self._config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        """
        Load configuration from file.

        Returns:
            AppConfig object with loaded or default values.

        Raises:
            ValueError: If the configuration file contains invalid data.
        """
        if self._config is not None:
            return self._config

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if data is None:
                    # Empty YAML file, use defaults
                    self._config = AppConfig()
                else:
                    self._config = AppConfig(**data)
            except (yaml.YAMLError, ValueError) as e:
                raise ValueError(
                    f"Invalid configuration file at {self.config_path}: {e}"
                ) from e
        else:
            # Create default configuration
            self._config = AppConfig()
            self.save(self._config)

        return self._config

    def save(self, config: AppConfig) -> None:
        """
        Save configuration to file.

        Args:
            config: AppConfig object to save.
        """
        self._config = config

        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                config.model_dump(),
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

    def get(self) -> AppConfig:
        """
        Get the current configuration (loads if not already loaded).

        Returns:
            Current AppConfig object.
        """
        if self._config is None:
            return self.load()
        return self._config
