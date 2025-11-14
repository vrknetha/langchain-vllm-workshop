"""Configuration management for Career Transition Advisor."""

import os
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # RunPod/vLLM Configuration
    RUNPOD_ENDPOINT_URL: str
    RUNPOD_API_KEY: SecretStr

    # Firecrawl Configuration
    FIRECRAWL_API_KEY: str

    # LLM Configuration
    MODEL_NAME: str = "NousResearch/Hermes-2-Pro-Mistral-7B"
    MAX_COMPLETION_TOKENS: int = 2048
    TEMPERATURE: float = 0.7

    def __init__(self):
        """Load and validate environment variables."""
        # RunPod Configuration
        self.RUNPOD_ENDPOINT_URL = self._get_required_env("RUNPOD_ENDPOINT_URL")
        runpod_api_key = self._get_required_env("RUNPOD_API_KEY")
        self.RUNPOD_API_KEY = SecretStr(runpod_api_key)

        # Firecrawl Configuration
        self.FIRECRAWL_API_KEY = self._get_required_env("FIRECRAWL_API_KEY")

        # Optional LLM overrides
        self.MODEL_NAME = os.getenv("MODEL_NAME", self.MODEL_NAME)
        self.MAX_COMPLETION_TOKENS = int(
            os.getenv("MAX_COMPLETION_TOKENS", str(self.MAX_COMPLETION_TOKENS))
        )
        self.TEMPERATURE = float(
            os.getenv("TEMPERATURE", str(self.TEMPERATURE))
        )

    @staticmethod
    def _get_required_env(key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"{key} environment variable is required")
        return value


# Global configuration instance
config = Config()
