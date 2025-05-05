from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.config import ALGORITHM, JWT_EXPIRATION_MINUTES, SECRET_KEY
from src.database.database import get_db
from src.database.models import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Define a sanitized user response model
class UserResponse(BaseModel):
    id: int
    username: str
    budget: float
    role: str

    class Config:
        orm_mode = True
        from_attributes = True

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserResponse:
    """Retrieve the current authenticated user based on the token."""
    try:
        print(f"Token received: {token}")  # Debug: Print the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload decoded: {payload}")  # Debug: Print the payload
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debug: Print the error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse.from_orm(user)

def is_admin(current_user: User = Depends(get_current_user)):
    """
    Verifies if the current user has an admin role.

    Args:
        current_user (User): The user object retrieved from the dependency injection.

    Raises:
        HTTPException: If the user's role is not "admin", an HTTP 403 Forbidden exception is raised.

    Returns:
        User: The current user object if the user has an admin role.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user

# Function to create an access token
def create_access_token(data: dict):
    """
    Generates a JSON Web Token (JWT) for authentication.

    Args:
        data (dict): A dictionary containing the payload data for the token. 
                     Must include a "sub" key representing the subject (e.g., user ID).

    Returns:
        str: The encoded JWT as a string.

    Raises:
        KeyError: If the "sub" key is not present in the input data.

    Notes:
        - The token includes an expiration time ("exp") and a subject ("sub").
        - The expiration time is calculated based on the current UTC time and 
          the JWT_EXPIRATION_MINUTES constant.
        - The token is signed using the SECRET_KEY and the specified ALGORITHM.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire, "sub": data["sub"]})  # Ensure "sub" is included
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt