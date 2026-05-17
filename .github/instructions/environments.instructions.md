---
applyTo: "src/**/config/**/*.py,src/**/*config*.py,src/**/*settings*.py"
---

## Purpose

Guide Copilot for environment configuration: dev/staging/prod settings, secret
injection, and environment-aware behaviour using pydantic-settings.

## Guidelines

### Settings Structure

- Use `pydantic-settings` `BaseSettings` as the single source of truth for all config.
- Load settings once at application startup; inject via dependency injection, not
  global imports.
- Define a precise type for every setting; avoid bare `str` for structured values
  (URLs, paths, enums).
- Provide sensible defaults only for non-sensitive, development-appropriate values.

### Environment Separation

- Use `APP_ENV` as the discriminator (`development`, `staging`, `production`).
- Never share secrets between environments; use separate vaults or secret namespaces.
- Log the active environment at startup; never log secret values.
- Use feature flags to gate experimental behaviour in non-production environments.

### Secret Injection

- Load secrets from environment variables; support `.env` files for local development
  only.
- Mark secret fields with `pydantic.SecretStr` to prevent accidental logging.
- Validate all required secrets at startup; raise a clear error if any are missing.
- Add `.env` to `.gitignore`; provide `.env.example` with placeholder values only.

### Testing

- Provide a `TestSettings` override with safe defaults for unit tests.
- Never use production credentials in tests; use mock or ephemeral services.

## Examples

```python
from functools import lru_cache
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Attributes:
        app_env: Active environment name (development, staging, production).
        database_url: SQLAlchemy-compatible database connection string.
        secret_key: JWT signing secret; loaded from environment only.
        debug: Enable debug mode; forced to False in production.
    """

    app_env: str = "development"
    database_url: str = "sqlite:///./dev.db"
    secret_key: SecretStr
    debug: bool = True

    @field_validator("debug", mode="before")
    @classmethod
    def force_no_debug_in_prod(cls, v: bool, info) -> bool:
        """Disable debug mode automatically in production."""
        if info.data.get("app_env") == "production":
            return False
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  """Build and cache application settings for dependency injection."""
  return Settings()
```
