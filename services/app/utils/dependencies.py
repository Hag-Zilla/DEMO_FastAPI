"""Shared dependencies and utility functions."""

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Annotated

from fastapi import Depends, HTTPException, status

from ..core.enums import UserRole
from ..core.security import get_current_user
from ..database.models.user import User as UserModel


# ============================================================================
# PUBLIC FUNCTIONS
# ============================================================================


def get_admin_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    """Dependency to ensure the current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user


def get_admin_or_moderator_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    """Dependency to ensure the current user is an admin or moderator."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MODERATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user
