from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.models import User as UserModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from src.config import ALGORITHM, SECRET_KEY
from datetime import datetime, timedelta, timezone
from src.config import JWT_EXPIRATION_MINUTES

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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise Exception("Invalid authentication credentials") from e

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[Session, Depends(get_db)]
                           ) -> UserModel:
    """
    Dependency to retrieve the current authenticated user from the JWT token.
    - Decodes the JWT token and extracts the username (sub claim).
    - Fetches the user from the database.
    - Raises HTTP 401 if credentials are invalid or user not found.
    - Raises HTTP 403 if the user account is disabled.
    - Returns the User SQLAlchemy model instance if authentication is successful.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                          )
    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user  # Return the SQLAlchemy model instance directly

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


def is_admin(current_user: Annotated[UserModel, Depends(get_current_user)]):
    """
    Dependency to ensure the current user has admin privileges.
    Raises HTTP 403 if the user is not an admin.
    Returns the current user if authorized.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "sub": data["sub"]})  # Ensure "sub" is included
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
