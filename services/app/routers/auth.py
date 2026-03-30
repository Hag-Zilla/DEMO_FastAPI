"""Authentication and token router."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.enums import UserStatus
from ..core.logging import get_logger
from ..core.security import authenticate_user, create_access_token
from ..database.session import get_db
from ..schemas.common import Token

logger = get_logger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/token", name="Login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate user and return access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Failed login attempt for username: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != UserStatus.ACTIVE:
        logger.warning(
            "Login attempt with non-active account: %s (status: %s)",
            form_data.username,
            user.status,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("User logged in: %s", user.username)
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
