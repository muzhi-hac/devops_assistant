"""OpenAI client wrapper for Parallax OpsPilot."""
from typing import Iterator

from openai import APIConnectionError, OpenAI

from .config import AppConfig
from .prompts import GEN_COMMAND_SYSTEM_PROMPT


class ParallaxConnectionError(Exception):
    """Raised when connection to Parallax server fails."""

    def __init__(self, message: str = "Failed to connect to Parallax server.") -> None:
        super().__init__(message)
        self.message = message


class ParallaxClient:
    """Client for interacting with Parallax inference server."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize the Parallax client.

        Args:
            config: Application configuration containing API base URL, API key, and model name.
        """
        self.config = config
        self.client = OpenAI(
            base_url=config.api_base,
            api_key=config.api_key,
        )

    def generate_command_stream(
        self, query: str, system_info: str
    ) -> Iterator[str]:
        """
        Generate shell command using streaming API.

        Args:
            query: Natural language query from the user.
            system_info: System information (OS and shell) from get_system_info().

        Yields:
            Chunks of the generated command as strings.

        Raises:
            ParallaxConnectionError: If connection to Parallax server fails.
        """
        # Construct user message with query and system info
        user_message = f"Environment: {system_info}\n\nUser request: {query}"

        messages = [
            {"role": "system", "content": GEN_COMMAND_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        try:
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                stream=True,
                temperature=0.1,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except APIConnectionError as e:
            raise ParallaxConnectionError(
                f"Failed to connect to Parallax server at {self.config.api_base}. "
                "Is Parallax running? Please check if the server is started and accessible."
            ) from e

