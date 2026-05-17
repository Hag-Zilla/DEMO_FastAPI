# Scenario: Pydantic-Settings Configuration

## Prompt

Set up a pydantic-settings configuration class for a FastAPI app with development,
staging, and production environments. Include database URL, JWT secret key, and a
debug flag that is forced to False in production.

## Expected Behavior

- Uses `pydantic-settings` `BaseSettings` as the single source of truth
- Marks `secret_key` as `SecretStr` to prevent accidental logging
- Forces `debug=False` in production via a field validator or model validator
- Provides a `get_settings()` factory with `@lru_cache` for dependency injection
- No global `settings = Settings()` at module level

## Must Include

- `SecretStr` on the secret field
- A validator (`@field_validator` or `model_validator`) enforcing `debug=False` in production
- `@lru_cache` on the settings factory function
- `model_config` with `env_file` set

## Must Avoid

- Hardcoded secrets or passwords in any field default value
- Global module-level `settings = Settings()` (use `Depends(get_settings)`)
- Bare `str` type for the secret key field
- Missing `.env.example` recommendation
