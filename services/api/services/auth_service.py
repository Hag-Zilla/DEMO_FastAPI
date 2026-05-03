"""AuthService: authentication orchestration, decoupled from business logic."""

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from services.api.auth.schemas import Token
from services.api.core.config import settings
from services.api.core.enums import UserStatus
from services.api.core.logging import get_logger
from services.api.core.metrics import LOGIN_FAILURE, LOGIN_SUCCESS
from services.api.core.security import (
    authenticate_user,
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    get_password_hash,
)
from services.api.database.models.user import User

logger = get_logger(__name__)


class AuthService:
    """Service handling authentication and token issuance.

    This service is the single place that knows how user credentials map to
    JWT tokens.  Business routers remain ignorant of JWT internals; they only
    receive a fully-formed Token or an exception.
    """

    @staticmethod
    def login_user(db: Session, username: str, password: str) -> Optional[Token]:
        """Authenticate user and return a signed JWT Token.

        Args:
            db: Active SQLAlchemy session.
            username: Supplied username.
            password: Plain-text password.

        Returns:
            Token if credentials are valid and account is ACTIVE; None if
            credentials are wrong.

        Raises:
            ValueError: If the account exists but is not ACTIVE.
        """
        user = authenticate_user(db, username, password)
        if not user:
            logger.warning("Failed login attempt for username: %s", username)
            LOGIN_FAILURE.inc()
            return None

        if user.status != UserStatus.ACTIVE:
            logger.warning(
                "Login attempt with non-active account: %s (status: %s)",
                username,
                user.status,
            )
            LOGIN_FAILURE.inc()
            raise ValueError("User account is not active")

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
        )
        LOGIN_SUCCESS.inc()
        logger.info("User logged in successfully: %s", username)
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def verify_user_active(user: User) -> bool:
        """Return True when the user account is ACTIVE."""
        return user.status == UserStatus.ACTIVE

    @staticmethod
    def get_token_expiration() -> timedelta:
        """Return the configured JWT expiration duration."""
        return timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    @staticmethod
    def request_password_reset(db: Session, username: str) -> str | None:
        """Create a password-reset token for an active user, if it exists."""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.info("Password reset requested for unknown user: %s", username)
            return None
        if user.status != UserStatus.ACTIVE:
            logger.info(
                "Password reset requested for non-active user: %s (status=%s)",
                username,
                user.status,
            )
            return None
        return create_password_reset_token(username)

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Reset password using a valid recovery token."""
        username = decode_password_reset_token(token)
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning("Password reset token for unknown user: %s", username)
            return False
        user.hashed_password = get_password_hash(new_password)  # type: ignore[assignment]
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Password reset completed for user: %s", username)
        return True
