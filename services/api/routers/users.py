"""User management router."""

from typing import cast

from fastapi import APIRouter, HTTPException, Query, status

from ..core.config import settings
from ..core.exceptions import ResourceNotFoundException, ValidationException
from ..core.logging import get_logger
from ..core.enums import UserStatus
from ..database.models.user import User as UserModel
from ..schemas.common import ListResponse
from ..schemas.user import UserCreate, UserSelfUpdate, UserUpdate, UserResponse
from ..services.user_service import UserService
from ..utils.dependencies import (
    AdminOrModeratorDep,
    AdminUserDep,
    CurrentUserDep,
    SessionDep,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "/create",
    name="Create User",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: SessionDep):
    """Create a new standard user account (status: PENDING, awaiting admin approval)."""
    return UserService.create_user(db, user)


@router.post(
    "/create-active",
    name="Create User (Active)",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_active(user: UserCreate, db: SessionDep):
    """Create a new standard user account with ACTIVE status (development/testing only).

    This endpoint bypasses the normal approval workflow and is useful for
    development and testing. In production, use POST /create followed by approval.
    """
    if settings.ENVIRONMENT != "local":
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return UserService.create_user_active(db, user)


@router.get("/me", name="Read Current User", response_model=UserResponse)
def read_users_me(current_user: CurrentUserDep):
    """Return the authenticated user's profile data."""
    return current_user


@router.put("/update/", name="Self Update User", response_model=UserResponse)
def self_update_user(
    user_update: UserSelfUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Update the authenticated user's own profile fields."""
    return UserService.update_user_self(db, cast(str, current_user.id), user_update)


@router.put("/update/{user_id}/", name="Admin Update User", response_model=UserResponse)
def admin_update_user(
    user_id: str,
    user_update: UserUpdate,
    db: SessionDep,
    _admin: AdminUserDep,
):
    """Update any user fields by ID (admin only)."""
    return UserService.update_user_admin(db, user_id, user_update)


@router.delete(
    "/delete/{user_id}/", name="Delete User", status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: str,
    db: SessionDep,
    admin: AdminUserDep,
):
    """Delete a user by ID (admin only)."""
    UserService.delete_user(db, user_id, cast(str, admin.id))


@router.get("/", name="List Users", response_model=ListResponse[UserResponse])
def list_users(
    status_filter: UserStatus | None = Query(
        None,
        alias="status",
        description="Filter by user status (pending, active, or disabled)",
    ),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of results"
    ),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    db: SessionDep = None,  # type: ignore[assignment]
    _admin: AdminUserDep = None,  # type: ignore[assignment]
):
    """List all users with optional status filter and pagination (admin only)."""
    users = UserService.list_users(db, status_filter, limit, offset)
    return ListResponse[UserResponse](data=users, count=len(users))


@router.post(
    "/{user_id}/approve",
    name="Approve User",
    response_model=UserResponse,
)
def approve_user(
    user_id: str,
    db: SessionDep,
    moderator: AdminOrModeratorDep,
):
    """Approve a pending user (admin or moderator only).

    Sets the user's status from PENDING to ACTIVE.

    Args:
        user_id: ID of the user to approve.
        db: Database session.
        moderator: Current admin or moderator user.

    Returns:
        The updated User object.

    Raises:
        ResourceNotFoundException: If user with given ID not found.
        ValidationException: If user is not in PENDING status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.PENDING:
        raise ValidationException(
            f"User {user_id} is not in PENDING status (current: {user.status})"
        )

    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    logger.info("Moderator %s approved user %s", moderator.id, user_id)
    return user


@router.post(
    "/{user_id}/reject",
    name="Reject User",
    response_model=UserResponse,
)
def reject_user(
    user_id: str,
    db: SessionDep,
    moderator: AdminOrModeratorDep,
):
    """Reject a pending user (admin or moderator only).

    Sets the user's status from PENDING to DISABLED.

    Args:
        user_id: ID of the user to reject.
        db: Database session.
        moderator: Current admin or moderator user.

    Returns:
        The updated User object.

    Raises:
        ResourceNotFoundException: If user with given ID not found.
        ValidationException: If user is not in PENDING status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.PENDING:
        raise ValidationException(
            f"User {user_id} is not in PENDING status (current: {user.status})"
        )

    user.status = UserStatus.DISABLED
    db.commit()
    db.refresh(user)
    logger.info("Moderator %s rejected user %s", moderator.id, user_id)
    return user


@router.post(
    "/{user_id}/disable",
    name="Disable User",
    response_model=UserResponse,
)
def disable_user(
    user_id: str,
    db: SessionDep,
    moderator: AdminOrModeratorDep,
):
    """Disable an active user (admin or moderator only).

    Sets the user's status from ACTIVE to DISABLED.

    Args:
        user_id: ID of the user to disable.
        db: Database session.
        moderator: Current admin or moderator user.

    Returns:
        The updated User object.

    Raises:
        ResourceNotFoundException: If user with given ID not found.
        ValidationException: If user is not in ACTIVE status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.ACTIVE:
        raise ValidationException(
            f"Cannot disable user {user_id}: user is not ACTIVE (current: {user.status})"
        )

    user.status = UserStatus.DISABLED
    db.commit()
    db.refresh(user)
    logger.info("Moderator %s disabled user %s", moderator.id, user_id)
    return user


@router.post(
    "/{user_id}/reactivate",
    name="Reactivate User",
    response_model=UserResponse,
)
def reactivate_user(
    user_id: str,
    db: SessionDep,
    moderator: AdminOrModeratorDep,
):
    """Reactivate a disabled user (admin or moderator only).

    Sets the user's status from DISABLED to ACTIVE.

    Args:
        user_id: ID of the user to reactivate.
        db: Database session.
        moderator: Current admin or moderator user.

    Returns:
        The updated User object.

    Raises:
        ResourceNotFoundException: If user with given ID not found.
        ValidationException: If user is not in DISABLED status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.DISABLED:
        raise ValidationException(
            f"Cannot reactivate user {user_id}: user is not DISABLED (current: {user.status})"
        )

    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    logger.info("Moderator %s reactivated user %s", moderator.id, user_id)
    return user
