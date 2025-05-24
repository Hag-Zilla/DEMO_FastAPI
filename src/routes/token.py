from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from jose import jwt
from sqlalchemy.orm import Session

from src.config import ALGORITHM, JWT_EXPIRATION_MINUTES, SECRET_KEY
from src.database.database import get_db
from src.database.models import User
from src.password_manager import verify_password

router = APIRouter()

################### FUNCTIONS ###################

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

################### ROUTES ###################

@router.post("/", name="Login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
                                 db: Annotated[Session, Depends(get_db)]
                                 ):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password) or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}