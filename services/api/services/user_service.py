"""User management service encapsulating user CRUD and admin operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from services.api.core.exceptions import (
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
    ValidationException,
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
    def _check_username_uniqueness(
        db: Session, username: str, exclude_user_id: str | None = None
    ) -> None:
        """Raise ConflictException if username is already taken.

        Args:
            db: Database session.
            username: Username to check.
            exclude_user_id: Optional user ID to exclude (for updates).

        Raises:
            ConflictException: If another user already has this username.
        """
        query = db.query(User).filter(User.username == username)
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        if query.first():
            logger.warning("Username already taken: %s", username)
            raise ConflictException(f"Username '{username}' already taken")

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
        UserService._check_username_uniqueness(db, user.username)

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
        UserService._check_username_uniqueness(db, user.username)

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
    def count_users(db: Session, status_filter: Optional[UserStatus] = None) -> int:
        """Return the total count of users matching the given status filter."""
        query = db.query(User)
        if status_filter is not None:
            query = query.filter(User.status == status_filter)  # type: ignore[arg-type]
        return query.count()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
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
        db: Session, user_id: str, user_update: UserSelfUpdate
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
            UserService._check_username_uniqueness(
                db, user_update.username, exclude_user_id=user_id
            )
            user.username = user_update.username  # type: ignore[assignment]

        # Update fields
        if user_update.budget is not None:
            user.budget = user_update.budget  # type: ignore[assignment]
        if user_update.password:
            user.hashed_password = get_password_hash(  # type: ignore[assignment]
                user_update.password
            )

        db.commit()
        db.refresh(user)
        logger.info("User %s updated their profile", user_id)
        return user

    @staticmethod
    def update_user_admin(db: Session, user_id: str, user_update: UserUpdate) -> User:
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
            UserService._check_username_uniqueness(
                db, user_update.username, exclude_user_id=user_id
            )
            user.username = user_update.username  # type: ignore[assignment]

        # Update fields
        if user_update.budget is not None:
            user.budget = user_update.budget  # type: ignore[assignment]
        if user_update.status is not None:
            user.status = user_update.status  # type: ignore[assignment]
        if user_update.password:
            user.hashed_password = get_password_hash(  # type: ignore[assignment]
                user_update.password
            )
        if user_update.role is not None:
            user.role = user_update.role  # type: ignore[assignment]

        db.commit()
        db.refresh(user)
        logger.info("Admin updated user %s", user_id)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str, admin_id: str) -> None:
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
    def _transition_status(
        db: Session,
        user_id: str,
        from_status: UserStatus,
        to_status: UserStatus,
        action_label: str,
    ) -> User:
        """Fetch user, assert current status, set new status, commit.

        Args:
            db: Database session.
            user_id: ID of the user whose status is being changed.
            from_status: Expected current status (raises ValidationException if wrong).
            to_status: Target status to set.
            action_label: Human-readable name for logging (e.g. "approve").

        Returns:
            Updated User object.

        Raises:
            ResourceNotFoundException: If user not found.
            ValidationException: If current status does not match from_status.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException(f"User with id {user_id} not found")
        if user.status != from_status:
            raise ValidationException(
                f"Cannot {action_label} user {user_id}: "
                f"expected {from_status.value}, got {user.status}"
            )
        user.status = to_status  # type: ignore[assignment]
        db.commit()
        db.refresh(user)
        logger.info(
            "User %s %sd (status: %s → %s)",
            user_id,
            action_label,
            from_status.value,
            to_status.value,
        )
        return user

    @staticmethod
    def approve_user(db: Session, user_id: str) -> User:
        """Approve a PENDING user → ACTIVE."""
        return UserService._transition_status(
            db, user_id, UserStatus.PENDING, UserStatus.ACTIVE, "approve"
        )

    @staticmethod
    def reject_user(db: Session, user_id: str) -> User:
        """Reject a PENDING user → DISABLED."""
        return UserService._transition_status(
            db, user_id, UserStatus.PENDING, UserStatus.DISABLED, "reject"
        )

    @staticmethod
    def disable_user(db: Session, user_id: str) -> User:
        """Disable an ACTIVE user → DISABLED."""
        return UserService._transition_status(
            db, user_id, UserStatus.ACTIVE, UserStatus.DISABLED, "disable"
        )

    @staticmethod
    def reactivate_user(db: Session, user_id: str) -> User:
        """Reactivate a DISABLED user → ACTIVE."""
        return UserService._transition_status(
            db, user_id, UserStatus.DISABLED, UserStatus.ACTIVE, "reactivate"
        )
