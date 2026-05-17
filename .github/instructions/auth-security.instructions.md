---
applyTo: "src/**/auth/**/*.py,src/**/*auth*.py,src/**/*security*.py,src/**/*jwt*.py"
---

## Purpose

Guide Copilot for authentication and authorization code: JWT, OAuth2, RBAC patterns,
and secret management in FastAPI applications.

## Guidelines

### JWT and Token Handling

- Validate JWT signatures on every request; never trust payload claims without
  verification.
- Set short expiry on access tokens (`exp` <= 15 min); use refresh tokens for sessions.
- Never log token values, even at DEBUG level.
- Store `SECRET_KEY` via environment variables; never hardcode it.

### OAuth2 with FastAPI

- Use `fastapi.security.OAuth2PasswordBearer` as the dependency for protected routes.
- Inject auth via `Depends(get_current_user)`; never check tokens inline in route
  handlers.
- Return HTTP 401 for invalid credentials, HTTP 403 for insufficient permissions;
  never HTTP 404, to avoid information leakage.

### Role-Based Access Control

- Define roles as an `Enum`; check permissions with a reusable `require_role()`
  dependency.
- Enforce least privilege by default: deny all, then grant explicitly.
- Log all authorization failures with user ID and requested resource, not token values.

### Secret Management

- Use `pydantic-settings` to load and validate all secrets at startup; fail fast if
  any are missing.
- Mark secret fields with `pydantic.SecretStr` to prevent accidental logging.
- Prefer a vault solution (HashiCorp Vault, AWS Secrets Manager) in production.
- Design the app to accept multiple valid signing keys to support zero-downtime
  rotation.

## Examples

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class AuthSettings(BaseSettings):
    """Settings required for JWT verification."""

    secret_key: str


def get_secret_key() -> str:
    """Return JWT secret key from environment-backed settings."""
    return AuthSettings().secret_key


def create_access_token(
    subject: str,
    secret_key: str,
    expires_minutes: int = 15,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject (e.g., user ID).
        secret_key: HMAC signing secret; load from environment only.
        expires_minutes: Token lifetime in minutes.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode({"sub": subject, "exp": expire}, secret_key, algorithm="HS256")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    secret_key: str = Depends(get_secret_key),
) -> str:
    """Validate a JWT token and return the subject claim.

    Args:
        token: Bearer token extracted from the Authorization header.

    Returns:
        Subject claim (user ID) from the validated token.

    Raises:
        HTTPException: HTTP 401 if token is invalid or expired.
    """
    try:
      payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```
