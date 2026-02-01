from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "AquaHub API"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str = "postgresql://aquahub:aquahub_secret@db:5432/aquahub"

    # CORS
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:3000"]

    # ML Models
    ml_model_path: str = "app/ml/models"

    # Twitter API
    twitter_api_key: Optional[str] = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=('settings_',)
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
