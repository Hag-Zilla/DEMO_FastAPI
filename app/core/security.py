"""Authentication and security utilities."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.enums import UserRole, UserStatus
from app.core.logging import get_logger
from app.database.session import get_db
from app.database.models.user import User as UserModel

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def decode_jwt_token(token: str) -> dict:
    """Decode and return the payload of a JWT token."""
    try:
        # settings.SECRET_KEY is a pydantic SecretStr; pass its raw value to PyJWT
        secret = (
            settings.SECRET_KEY.get_secret_value()
            if hasattr(settings.SECRET_KEY, "get_secret_value")
            else settings.SECRET_KEY
        )
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except InvalidTokenError as e:
        raise AuthenticationException("Invalid authentication credentials") from e


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    """Dependency to retrieve the current authenticated user from the JWT token.

    Decodes JWT token, extracts username, fetches user from database.
    Raises 401 if credentials invalid. Raises 403 if account not active.

    Returns:
        UserModel: The authenticated user if successful.

    Raises:
        AuthenticationException: If token is invalid or user not found.
        AuthorizationException: If user account is not active.
    """
    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")  # type: ignore[assignment]
        if username is None:
            logger.warning("JWT token missing 'sub' claim")
            raise AuthenticationException()
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            logger.warning("User not found for token: %s", username)
            raise AuthenticationException()
        if user.status != UserStatus.ACTIVE:
            logger.warning(
                "Login attempt with non-active account: %s (status: %s)",
                username,
                user.status,
            )
            raise AuthorizationException("User account is not active")
        return user  # Return the SQLAlchemy model instance directly

    except (AuthenticationException, AuthorizationException):
        raise
    except Exception as e:
        logger.error("Unexpected error in get_current_user: %s", e, exc_info=True)
        raise AuthenticationException() from e


def is_admin(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """Dependency to ensure the current user has admin privileges.

    Raises HTTP 403 if the user is not an admin.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        UserModel: The current user if they are an admin.

    Raises:
        AuthorizationException: If user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning("Unauthorized access attempt by user %s", current_user.id)
        raise AuthorizationException(
            "You do not have permission to perform this action."
        )
    return current_user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a JSON Web Token (JWT) for authentication.

    Args:
        data: Dictionary containing payload data (must include 'sub' key).
        expires_delta: Optional timedelta for token expiration. If not provided,
            the token will expire based on JWT_EXPIRATION_MINUTES constant.

    Returns:
        str: The encoded JWT token.

    Raises:
        KeyError: If the 'sub' key is not present in input data.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRATION_MINUTES
        )
    to_encode.update({"exp": expire, "sub": data["sub"]})  # Ensure "sub" is included
    secret = (
        settings.SECRET_KEY.get_secret_value()
        if hasattr(settings.SECRET_KEY, "get_secret_value")
        else settings.SECRET_KEY
    )
    encoded_jwt = jwt.encode(
        to_encode,
        secret,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password."""
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):  # type: ignore[arg-type]
        return None
    return user
