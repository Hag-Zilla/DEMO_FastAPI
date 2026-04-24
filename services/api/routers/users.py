"""User management router."""

from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..core.exceptions import ResourceNotFoundException
from ..core.logging import get_logger
from ..core.security import get_current_user
from ..core.enums import UserStatus
from ..database.session import get_db
from ..utils.dependencies import get_admin_user, get_admin_or_moderator_user
from ..database.models.user import User as UserModel
from ..schemas.user import UserCreate, UserSelfUpdate, UserUpdate, UserResponse
from ..services.user_service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "/create",
    name="Create User",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new standard user account (status: PENDING, awaiting admin approval)."""
    return UserService.create_user(db, user)


@router.post(
    "/create-active",
    name="Create User (Active)",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_active(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new standard user account with ACTIVE status (development/testing only).

    This endpoint bypasses the normal approval workflow and is useful for
    development and testing. In production, use POST /create followed by approval.
    """
    return UserService.create_user_active(db, user)


@router.get("/me", name="Read Current User", response_model=UserResponse)
def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Return the authenticated user's profile data."""
    return current_user


@router.put("/update/", name="Self Update User", response_model=UserResponse)
def self_update_user(
    user_update: UserSelfUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Update the authenticated user's own profile fields."""
    return UserService.update_user_self(db, cast(str, current_user.id), user_update)


@router.put("/update/{user_id}/", name="Admin Update User", response_model=UserResponse)
def admin_update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Update any user fields by ID (admin only)."""
    return UserService.update_user_admin(db, user_id, user_update)


@router.delete(
    "/delete/{user_id}/", name="Delete User", status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Delete a user by ID (admin only)."""
    UserService.delete_user(db, user_id, cast(str, admin.id))


@router.get("/", name="List Users", response_model=List[UserResponse])
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
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
    _admin: Annotated[UserModel, Depends(get_admin_user)] = None,  # type: ignore[assignment]
):
    """List all users with optional status filter and pagination (admin only)."""
    return UserService.list_users(db, status_filter, limit, offset)


@router.post(
    "/{user_id}/approve",
    name="Approve User",
    response_model=UserResponse,
)
def approve_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(get_admin_or_moderator_user)],
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
        ValueError: If user is not in PENDING status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.PENDING:
        raise ValueError(
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
    db: Annotated[Session, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(get_admin_or_moderator_user)],
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
        ValueError: If user is not in PENDING status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.PENDING:
        raise ValueError(
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
    db: Annotated[Session, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(get_admin_or_moderator_user)],
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
        ValueError: If user is not in ACTIVE status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.ACTIVE:
        raise ValueError(
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
    db: Annotated[Session, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(get_admin_or_moderator_user)],
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
        ValueError: If user is not in DISABLED status.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    if user.status != UserStatus.DISABLED:
        raise ValueError(
            f"Cannot reactivate user {user_id}: user is not DISABLED (current: {user.status})"
        )

    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    logger.info("Moderator %s reactivated user %s", moderator.id, user_id)
    return user
