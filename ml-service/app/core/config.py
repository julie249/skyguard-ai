"""
ML Microservice Configuration Module.
Loads environment variables and sets core service paths.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ml_host: str = "0.0.0.0"
    ml_port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"
    model_store_dir: str = "models_store"
    # Set to False to skip the LSTM model on low-RAM hosts (Render free tier < 512 MB)
    enable_lstm: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
