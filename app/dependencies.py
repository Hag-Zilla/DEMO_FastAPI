"""Shared dependencies for the application."""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from .core.security import get_current_user
from .models.user import User as UserModel


async def get_admin_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
) -> UserModel:
    """Dependency to ensure the current user is an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user
