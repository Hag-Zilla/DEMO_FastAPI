"""Common/shared Pydantic schemas.

Token and TokenData have moved to api.auth.schemas.
This module re-exports them for backward compatibility.
"""

from services.api.auth.schemas import Token, TokenData  # noqa: F401

__all__ = ["Token", "TokenData"]
