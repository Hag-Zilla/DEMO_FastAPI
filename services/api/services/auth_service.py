"""Auth service — re-exported from the dedicated auth sub-package.

All real implementation lives in api.auth.service.
This module is kept for import-path backward compatibility.
"""

from api.auth.service import AuthService  # noqa: F401

__all__ = ["AuthService"]
