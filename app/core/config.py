"""Application configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    SECRET_KEY: str = "your_default_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./expense_tracker.db"

    # Application Configuration
    APP_NAME: str = "Expense Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Single instance of settings
settings = Settings()
