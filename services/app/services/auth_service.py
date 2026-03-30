"""Authentication service encapsulating token and user verification logic."""

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserStatus
from app.core.logging import get_logger
from app.core.security import authenticate_user, create_access_token
from app.database.models.user import User
from app.schemas.common import Token

logger = get_logger(__name__)


class AuthService:
    """Service handling authentication, token generation, and user verification."""

    @staticmethod
    def login_user(
        db: Session,
        username: str,
        password: str,
    ) -> Optional[Token]:
        """
        Authenticate user and generate access token.

        Args:
            db: Database session
            username: Username for authentication
            password: User password

        Returns:
            Token object with access_token and token_type, or None if auth fails

        Raises:
            ValueError: If user status is not ACTIVE
        """
        user = authenticate_user(db, username, password)
        if not user:
            logger.warning("Failed login attempt for username: %s", username)
            return None

        if user.status != UserStatus.ACTIVE:
            logger.warning(
                "Login attempt with non-active account: %s (status: %s)",
                username,
                user.status,
            )
            raise ValueError("User account is not active")

        logger.info("User logged in: %s", username)
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def verify_user_active(user: User) -> bool:
        """
        Verify if user account is active.

        Args:
            user: User model instance

        Returns:
            True if user is active, False otherwise
        """
        return user.status == UserStatus.ACTIVE

    @staticmethod
    def get_token_expiration() -> timedelta:
        """
        Get configured token expiration duration.

        Returns:
            Timedelta for token expiration
        """
        return timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
