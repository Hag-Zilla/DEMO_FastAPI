"""Auth sub-package — self-contained authentication module.

This package owns:
- JWT token creation and validation (via core/security primitives)
- Login endpoint (/api/v1/auth/token)
- AuthService: authentication orchestration
- Auth-specific Pydantic schemas (Token, TokenData)

Usage from the rest of the codebase:
    from services.api.auth import router      # mount in main.py
    from services.api.auth import AuthService  # if needed in other services
"""

from .router import router
from .service import AuthService

__all__ = ["router", "AuthService"]
