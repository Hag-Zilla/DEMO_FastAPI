"""User management router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictException, ResourceNotFoundException
from ..core.logging import get_logger
from ..core.security import get_current_user, get_password_hash
from ..core.enums import UserRole
from ..database.session import get_db
from ..utils.dependencies import get_admin_user
from ..database.models.user import User as UserModel
from ..schemas.user import UserCreate, UserUpdate, UserResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "/create",
    name="Create User",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Create a new standard user account."""
    # Check if username already exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        logger.warning("Attempt to create user with existing username: %s", user.username)
        raise ConflictException(f"Username '{user.username}' already taken")

    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        budget=user.budget,
        role=UserRole.USER,  # Force role to 'user' regardless of input
        disabled=False,  # Default to not disabled
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created: %s", user.username)
    return db_user


@router.get("/me", name="Read Current User", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Return the authenticated user's profile data."""
    return current_user


@router.put("/update/", name="Self Update User", response_model=UserResponse)
async def self_update_user(
    user_update: UserUpdate,
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
        user.username = user_update.username
    if user_update.budget is not None:
        user.budget = user_update.budget
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)

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
        user.username = user_update.username

    # Update fields
    if user_update.budget is not None:
        user.budget = user_update.budget
    if user_update.disabled is not None:
        user.disabled = user_update.disabled
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    if user_update.role is not None:
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    logger.info("Admin updated user %s", user_id)
    return user


@router.delete("/delete/{user_id}/", name="Delete User", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Delete a user by ID (admin only)."""
    del _admin
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise ResourceNotFoundException(f"User with id {user_id} not found")
    db.delete(user)
    db.commit()
    logger.info("Admin deleted user %s", user_id)
