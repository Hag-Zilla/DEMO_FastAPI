"""User management router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..core.exceptions import (
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
)
from ..core.logging import get_logger
from ..core.security import get_current_user, get_password_hash
from ..core.enums import UserRole, UserStatus
from ..database.session import get_db
from ..utils.dependencies import get_admin_user, get_admin_or_moderator_user
from ..database.models.user import User as UserModel
from ..schemas.user import UserCreate, UserSelfUpdate, UserUpdate, UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "/create",
    name="Create User",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new standard user account (status will be PENDING, awaiting admin approval)."""
    # Check if username already exists
    existing_user = (
        db.query(UserModel).filter(UserModel.username == user.username).first()
    )
    if existing_user:
        logger.warning(
            "Attempt to create user with existing username: %s", user.username
        )
        raise ConflictException(f"Username '{user.username}' already taken")

    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        budget=user.budget,
        role=UserRole.USER,  # Force role to 'user' regardless of input
        status=UserStatus.PENDING,  # New users start in PENDING status awaiting admin approval
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created with PENDING status: %s", user.username)
    return db_user


@router.get("/me", name="Read Current User", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Return the authenticated user's profile data."""
    return current_user


@router.put("/update/", name="Self Update User", response_model=UserResponse)
async def self_update_user(
    user_update: UserSelfUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Update the authenticated user's own profile fields."""
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise ResourceNotFoundException("User not found")

    # Check username uniqueness
    if user_update.username and user_update.username != user.username:
        existing_user = (
            db.query(UserModel)
            .filter(UserModel.username == user_update.username)
            .first()
        )
        if existing_user:
            logger.warning(
                "User %s tried to change username to existing one: %s",
                current_user.id,
                user_update.username,
            )
            raise ConflictException(f"Username '{user_update.username}' already taken")

    # Update fields
    if user_update.username:
        user.username = user_update.username  # type: ignore[assignment]
    if user_update.budget is not None:
        user.budget = user_update.budget  # type: ignore[assignment]
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)  # type: ignore[assignment]

    db.commit()
    db.refresh(user)
    logger.info("User %s updated their profile", current_user.id)
    return user


@router.put("/update/{user_id}/", name="Admin Update User", response_model=UserResponse)
async def admin_update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Update any user fields by ID (admin only)."""
    del _admin
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    # Check username uniqueness
    if user_update.username is not None:
        existing_user = (
            db.query(UserModel)
            .filter(
                UserModel.username == user_update.username,
                UserModel.id != user_id,
            )
            .first()
        )
        if existing_user:
            logger.warning(
                "Admin tried to change user %s username to existing one: %s",
                user_id,
                user_update.username,
            )
            raise ConflictException(f"Username '{user_update.username}' already taken")
        user.username = user_update.username  # type: ignore[assignment]

    # Update fields
    if user_update.budget is not None:
        user.budget = user_update.budget  # type: ignore[assignment]
    if user_update.status is not None:
        user.status = user_update.status  # type: ignore[assignment]
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)  # type: ignore[assignment]
    if user_update.role is not None:
        user.role = user_update.role  # type: ignore[assignment]

    db.commit()
    db.refresh(user)
    logger.info("Admin updated user %s", user_id)
    return user


@router.delete(
    "/delete/{user_id}/", name="Delete User", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Delete a user by ID (admin only)."""
    if admin.id == user_id:
        logger.warning("Admin %s attempted to delete own account", admin.id)
        raise AuthorizationException("Admin users cannot delete their own account")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")
    db.delete(user)
    db.commit()
    logger.info("Admin deleted user %s", user_id)


@router.get(
    "/",
    name="List Users by Status",
    response_model=List[UserResponse],
)
async def list_users_by_status(
    status_filter: UserStatus | None = Query(
        None,
        alias="status",
        description="Filter by user status (pending, active, or disabled)",
    ),
    db: Annotated[Session, Depends(get_db)] = None,  # type: ignore[assignment]
    _admin: Annotated[UserModel, Depends(get_admin_user)] = None,  # type: ignore[assignment]
):
    """List all users, optionally filtered by status (admin only).

    Args:
        status_filter: Optional filter for user status (pending, active, or disabled).
        db: Database session.
        _admin: Admin user (access already validated by dependency).

    Returns:
        List of User objects, optionally filtered by status.
    """
    del _admin  # Admin access already validated by dependency
    query = db.query(UserModel)

    if status_filter is not None:
        query = query.filter(UserModel.status == status_filter)  # type: ignore[arg-type]

    users = query.all()
    logger.info("Admin retrieved user list with filter: %s", status_filter)
    return users


@router.post(
    "/{user_id}/approve",
    name="Approve User",
    response_model=UserResponse,
)
async def approve_user(
    user_id: int,
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
async def reject_user(
    user_id: int,
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
async def disable_user(
    user_id: int,
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
async def reactivate_user(
    user_id: int,
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
