"""Application configuration management using Pydantic Settings."""

from typing import Any, Literal, Optional

from pydantic import AnyUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    SECRET_KEY: SecretStr = Field(..., min_length=32)
    # Restrict signing algorithm to a vetted value.
    ALGORITHM: Literal["HS256"] = "HS256"
    JWT_EXPIRATION_MINUTES: int = Field(30, ge=1)
    PASSWORD_RESET_EXPIRATION_MINUTES: int = Field(60, ge=5)

    # Database Configuration
    DATABASE_URL: str = Field(..., min_length=1)

    # Redis Configuration (optional – falls back to in-memory if absent)
    REDIS_URL: Optional[str] = None

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # CORS configuration (comma-separated string accepted in env files)
    BACKEND_CORS_ORIGINS: list[AnyUrl] | str = Field(default_factory=list)

    # Application Configuration
    APP_NAME: str = Field(..., min_length=1)
    APP_VERSION: str = Field(..., min_length=1)
    DEBUG: bool

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        """Allow comma-separated CORS origins in environment values."""
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return value
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

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
