"""Auth sub-package — self-contained authentication module.

This package owns:
- JWT token creation and validation (via core/security primitives)
- Login endpoint (/api/v1/auth/token)
- AuthService: authentication orchestration
- Auth-specific Pydantic schemas (Token, TokenData)

Usage from the rest of the codebase:
    from services.api.auth import router      # mount in main.py
"""

from .router import router

__all__ = ["router"]
