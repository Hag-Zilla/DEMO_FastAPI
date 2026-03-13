"""Application configuration management using Pydantic Settings."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    ALGORITHM: str = Field(..., min_length=1)
    JWT_EXPIRATION_MINUTES: int = Field(30, ge=1)

    # Database Configuration
    DATABASE_URL: str = Field(..., min_length=1)

    # Application Configuration
    APP_NAME: str = Field(..., min_length=1)
    APP_VERSION: str = Field(..., min_length=1)
    DEBUG: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

# Single instance of settings (typed to help static analyzers)
settings: Settings = Settings()
