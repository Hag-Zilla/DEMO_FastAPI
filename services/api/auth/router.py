"""Auth router — login endpoint delegating entirely to AuthService."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestFormStrict

from services.api.auth.schemas import (
    PasswordRecoveryRequest,
    PasswordRecoveryResponse,
    PasswordResetRequest,
    Token,
)
from services.api.services.auth_service import AuthService
from services.api.core.config import settings
from services.api.core.exceptions import AuthenticationException
from services.api.core.logging import get_logger
from services.api.utils.dependencies import SessionDep

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", name="Login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    db: SessionDep,
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


@router.post(
    "/password-recovery",
    name="Password Recovery",
    response_model=PasswordRecoveryResponse,
)
def request_password_recovery(
    payload: PasswordRecoveryRequest,
    db: SessionDep,
) -> PasswordRecoveryResponse:
    """Request a password-reset token.

    Always returns a generic success message to avoid account enumeration.
    """
    token = AuthService.request_password_reset(db, payload.username)
    if settings.ENVIRONMENT == "local" and token:
        return PasswordRecoveryResponse(
            message="If the account exists, a reset token has been generated.",
            reset_token=token,
        )
    return PasswordRecoveryResponse(
        message="If the account exists, a reset token has been generated."
    )


@router.post(
    "/reset-password", name="Reset Password", status_code=status.HTTP_204_NO_CONTENT
)
def reset_password(
    payload: PasswordResetRequest,
    db: SessionDep,
) -> None:
    """Reset password from a recovery token."""
    try:
        success = AuthService.reset_password(db, payload.token, payload.new_password)
    except AuthenticationException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )
