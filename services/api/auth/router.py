"""Auth router — login endpoint delegating entirely to AuthService."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict
from sqlalchemy.orm import Session

from api.auth.schemas import Token
from api.auth.service import AuthService
from api.core.logging import get_logger
from api.database.session import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", name="Login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate user credentials and return a JWT access token."""
    try:
        token = AuthService.login_user(db, form_data.username, form_data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if token is None:
        logger.warning("Failed login attempt for username: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("User logged in: %s", form_data.username)
    return token
