"""Authentication and security utilities."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.orm import Session

from services.api.core.config import settings
from services.api.core.exceptions import AuthenticationException, AuthorizationException
from services.api.core.enums import UserRole, UserStatus
from services.api.core.logging import get_logger
from services.api.database.session import get_db
from services.api.database.models.user import User as UserModel

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Password hashing — Argon2 primary, bcrypt as legacy fallback for migrations
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

# Argon2id hash of a random password used to prevent username-enumeration via
# timing differences: we always run a full hash comparison even when the user
# does not exist, so the response time is the same in both cases.
DUMMY_HASH = (  # pragma: allowlist secret
    "$argon2id$v=19$m=65536,t=3,p=4"
    "$MjQyZWE1MzBjYjJlZTI0Yw"
    "$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    verified, _ = password_hash.verify_and_update(plain_password, hashed_password)
    return verified


def decode_jwt_token(token: str) -> dict:
    """Decode and return the payload of a JWT token."""
    try:
        # settings.SECRET_KEY is a pydantic SecretStr; pass its raw value to PyJWT
        secret: str = settings.SECRET_KEY.get_secret_value()  # pylint: disable=no-member
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except InvalidTokenError as e:
        raise AuthenticationException("Invalid authentication credentials") from e


def get_current_user(
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
    secret: str = settings.SECRET_KEY.get_secret_value()  # pylint: disable=no-member
    encoded_jwt = jwt.encode(
        to_encode,
        secret,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> UserModel | None:
    """Authenticate a user by username and password.

    Runs a full hash verification even when the user does not exist to prevent
    timing-based username enumeration. If the stored hash algorithm has been
    upgraded (bcrypt → argon2), the new hash is persisted transparently.
    """
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        # Prevent timing attacks: same cost whether username exists or not.
        password_hash.verify_and_update(password, DUMMY_HASH)
        return None
    verified, updated_hash = password_hash.verify_and_update(
        password,
        user.hashed_password,  # type: ignore[arg-type]
    )
    if not verified:
        return None
    if updated_hash:
        # Algorithm migration (e.g. bcrypt → argon2): persist the refreshed hash.
        user.hashed_password = updated_hash  # type: ignore[assignment]
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
