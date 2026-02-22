"""Authentication and security utilities."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.core.enums import UserRole
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationException("Invalid authentication credentials") from e


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    """
    Dependency to retrieve the current authenticated user from the JWT token.
    - Decodes the JWT token and extracts the username (sub claim).
    - Fetches the user from the database.
    - Raises HTTP 401 if credentials are invalid or user not found.
    - Raises HTTP 403 if the user account is disabled.
    - Returns the User SQLAlchemy model instance if authentication is successful.
    """
    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT token missing 'sub' claim")
            raise AuthenticationException()
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            logger.warning(f"User not found for token: {username}")
            raise AuthenticationException()
        if user.disabled:
            logger.warning(f"Login attempt with disabled account: {username}")
            raise AuthorizationException("User account is disabled")
        return user  # Return the SQLAlchemy model instance directly

    except (AuthenticationException, AuthorizationException):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise AuthenticationException() from e


def is_admin(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """
    Dependency to ensure the current user has admin privileges.
    Raises HTTP 403 if the user is not an admin.
    Returns the current user if authorized.
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Unauthorized access attempt by user {current_user.id}")
        raise AuthorizationException("You do not have permission to perform this action.")
    return current_user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Generates a JSON Web Token (JWT) for authentication.

    Args:
        data (dict): A dictionary containing the payload data for the token.
                     Must include a "sub" key representing the subject (e.g., user ID).
        expires_delta (timedelta | None): Optional. A timedelta object representing the
                                           desired expiration time for the token. If not
                                           provided, the token will expire based on the
                                           JWT_EXPIRATION_MINUTES constant.

    Returns:
        str: The encoded JWT as a string.

    Raises:
        KeyError: If the "sub" key is not present in the input data.

    Notes:
        - The token includes an expiration time ("exp") and a subject ("sub").
        - The expiration time is calculated based on the current UTC time and
          the JWT_EXPIRATION_MINUTES constant, or based on the provided expires_delta.
        - The token is signed using the SECRET_KEY and the specified ALGORITHM.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "sub": data["sub"]})  # Ensure "sub" is included
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password."""
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
