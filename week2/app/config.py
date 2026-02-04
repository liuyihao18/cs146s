"""
Configuration and settings management.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App metadata
    app_title: str = "Action Item Extractor"
    app_version: str = "1.0.0"

    # Database
    db_path: Path = Path(__file__).resolve().parents[1] / "data" / "app.db"

    # LLM
    ollama_host: str = "http://10.5.0.4:11434/"
    ollama_model: str = "llama3.1"
    enable_llm_extraction: bool = True

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
    )


settings = Settings()
