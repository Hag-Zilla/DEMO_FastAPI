"""Application configuration management using Pydantic Settings."""

from typing import Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    # Restrict signing algorithm to a vetted value.
    ALGORITHM: Literal["HS256"] = "HS256"
    JWT_EXPIRATION_MINUTES: int = Field(30, ge=1)

    # Database Configuration
    DATABASE_URL: str = Field(..., min_length=1)

    # Redis Configuration (optional – falls back to in-memory if absent)
    REDIS_URL: Optional[str] = None

    # Observability / error tracking
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "local"

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


# ============================================================================
# MODULE SETUP / EXPORTS
# ============================================================================

# Single instance of settings (typed to help static analyzers)
settings: Settings = Settings()  # type: ignore[call-arg]  # args loaded from env
