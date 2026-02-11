from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from sqlalchemy.orm import Session

from src.config import JWT_EXPIRATION_MINUTES
from src.database.database import get_db
from src.auth_manager import create_access_token, authenticate_user
from src.schemas import Token

router = APIRouter()

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

    access_token_expires = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires
                                       )
    
    return Token(access_token=access_token, token_type="bearer")