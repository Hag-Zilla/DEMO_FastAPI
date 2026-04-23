"""User management service encapsulating user CRUD and admin operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from services.api.core.exceptions import (
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
)
from services.api.core.enums import UserRole, UserStatus
from services.api.core.logging import get_logger
from services.api.core.security import get_password_hash
from services.api.database.models.user import User
from services.api.schemas.user import UserCreate, UserSelfUpdate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Service handling user CRUD operations, validation, and admin workflows."""

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Create a new standard user account (status will be PENDING, awaiting admin approval).

        Args:
            db: Database session
            user: UserCreate schema with username, password, budget

        Returns:
            Newly created User model instance

        Raises:
            ConflictException: If username already exists
        """
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            logger.warning(
                "Attempt to create user with existing username: %s", user.username
            )
            raise ConflictException(f"Username '{user.username}' already taken")

        hashed_password = get_password_hash(user.password)
        db_user = User(
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

    @staticmethod
    def create_user_active(db: Session, user: UserCreate) -> User:
        """
        Create a new standard user account with ACTIVE status (development/testing only).

        This bypasses the normal approval workflow. Useful for dev/test environments where
        you want immediate login capability without admin approval.

        Args:
            db: Database session
            user: UserCreate schema with username, password, budget

        Returns:
            Newly created User model instance

        Raises:
            ConflictException: If username already exists
        """
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            logger.warning(
                "Attempt to create user with existing username: %s", user.username
            )
            raise ConflictException(f"Username '{user.username}' already taken")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            hashed_password=hashed_password,
            budget=user.budget,
            role=UserRole.USER,  # Force role to 'user' regardless of input
            status=UserStatus.ACTIVE,  # Directly ACTIVE (dev/test only)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info("User created with ACTIVE status (dev/test): %s", user.username)
        return db_user

    @staticmethod
    def list_users(
        db: Session,
        status_filter: Optional[UserStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        """List all users with optional status filter and pagination."""
        query = db.query(User)
        if status_filter is not None:
            query = query.filter(User.status == status_filter)  # type: ignore[arg-type]
        return query.offset(offset).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Retrieve user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User model instance or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Retrieve user by username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            User model instance or None if not found
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_user_self(
        db: Session, user_id: int, user_update: UserSelfUpdate
    ) -> User:
        """
        Update the authenticated user's own profile fields.

        Args:
            db: Database session
            user_id: Current user ID
            user_update: UserSelfUpdate schema with optional fields

        Returns:
            Updated User model instance

        Raises:
            ResourceNotFoundException: If user not found
            ConflictException: If new username already exists
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException("User not found")

        # Check username uniqueness (if changed)
        if user_update.username and user_update.username != user.username:
            existing_user = (
                db.query(User).filter(User.username == user_update.username).first()
            )
            if existing_user:
                logger.warning(
                    "User %s tried to change username to existing one: %s",
                    user_id,
                    user_update.username,
                )
                raise ConflictException(
                    f"Username '{user_update.username}' already taken"
                )
            user.username = user_update.username  # type: ignore[assignment]

        # Update fields
        if user_update.budget is not None:
            user.budget = user_update.budget  # type: ignore[assignment]
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)  # type: ignore[assignment]

        db.commit()
        db.refresh(user)
        logger.info("User %s updated their profile", user_id)
        return user

    @staticmethod
    def update_user_admin(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """
        Update any user fields by ID (admin only).

        Args:
            db: Database session
            user_id: User ID to update
            user_update: UserUpdate schema with fields to update

        Returns:
            Updated User model instance

        Raises:
            ResourceNotFoundException: If user not found
            ConflictException: If new username already exists
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException(f"User with id {user_id} not found")

        # Check username uniqueness
        if user_update.username is not None:
            existing_user = (
                db.query(User)
                .filter(
                    User.username == user_update.username,
                    User.id != user_id,
                )
                .first()
            )
            if existing_user:
                logger.warning(
                    "Admin tried to change user %s username to existing one: %s",
                    user_id,
                    user_update.username,
                )
                raise ConflictException(
                    f"Username '{user_update.username}' already taken"
                )
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

    @staticmethod
    def delete_user(db: Session, user_id: int, admin_id: int) -> None:
        """
        Delete a user by ID (admin only).

        Args:
            db: Database session
            user_id: User ID to delete
            admin_id: Current admin user ID

        Raises:
            AuthorizationException: If admin tries to delete their own account
            ResourceNotFoundException: If user not found
        """
        if admin_id == user_id:
            logger.warning("Admin %s attempted to delete own account", admin_id)
            raise AuthorizationException("Admin users cannot delete their own account")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException(f"User with id {user_id} not found")
        db.delete(user)
        db.commit()
        logger.info("Admin deleted user %s", user_id)

    @staticmethod
    def list_users_by_status(
        db: Session, status_filter: Optional[UserStatus] = None
    ) -> List[User]:
        """
        List all users, optionally filtered by status (admin only).

        Args:
            db: Database session
            status_filter: Optional filter for user status

        Returns:
            List of User objects
        """
        query = db.query(User)
        if status_filter is not None:
            query = query.filter(User.status == status_filter)  # type: ignore[arg-type]
        users = query.all()
        logger.info("Admin retrieved user list with filter: %s", status_filter)
        return users

    @staticmethod
    def approve_user(db: Session, user_id: int) -> User:
        """
        Approve a pending user by changing status from PENDING to ACTIVE.

        Args:
            db: Database session
            user_id: ID of user to approve

        Returns:
            Updated User object with ACTIVE status

        Raises:
            ResourceNotFoundException: If user not found
            ConflictException: If user is not in PENDING status
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException(f"User with id {user_id} not found")

        if user.status != UserStatus.PENDING:
            raise ConflictException(
                f"Can only approve PENDING users; user is {user.status}"
            )

        user.status = UserStatus.ACTIVE  # type: ignore[assignment]
        db.commit()
        db.refresh(user)
        logger.info("User %s approved and set to ACTIVE", user_id)
        return user
