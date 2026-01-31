from pydantic_settings import BaseSettings
from functools import lru_cache


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
    model_path: str = "app/ml/models"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
