from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from jose import jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.config import ALGORITHM, JWT_EXPIRATION_MINUTES, SECRET_KEY
from src.database.database import get_db
from src.database.models import User
from src.password_manager import verify_password

router = APIRouter()

################### FUNCTIONS ###################

# Function to create an access token
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

################### MODELS ###################

class Token(BaseModel):
    access_token: str
    token_type: str

################### ROUTES ###################

@router.post("/", name="Login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
                                 db: Annotated[Session, Depends(get_db)]
                                 ) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")