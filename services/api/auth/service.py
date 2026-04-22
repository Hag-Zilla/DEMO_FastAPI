"""AuthService: authentication orchestration, decoupled from business logic."""

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from services.api.auth.schemas import Token
from services.api.core.config import settings
from services.api.core.enums import UserStatus
from services.api.core.logging import get_logger
from services.api.core.metrics import LOGIN_FAILURE, LOGIN_SUCCESS
from services.api.core.security import authenticate_user, create_access_token
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
