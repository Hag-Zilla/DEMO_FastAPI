"""Auth router — re-exported from the dedicated auth sub-package.

All real implementation lives in api.auth.router.
This module is kept for import-path backward compatibility.
"""

from api.auth.router import router  # noqa: F401

__all__ = ["router"]
