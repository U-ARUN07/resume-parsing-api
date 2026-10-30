"""Application configuration module using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/resume_parser_db"

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx"}

    # Environment & Server
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    @property
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Return resolved upload directory Path."""
        path = Path(self.UPLOAD_DIR)
        return path if path.is_absolute() else Path.cwd() / path


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
