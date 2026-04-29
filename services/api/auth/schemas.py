"""Auth-specific Pydantic schemas."""

from pydantic import Field
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    """Decoded JWT token payload."""

    username: str | None = None


class PasswordRecoveryRequest(BaseModel):
    """Request payload to initiate password recovery."""

    username: str = Field(..., min_length=3, max_length=50)


class PasswordRecoveryResponse(BaseModel):
    """Generic recovery response. Reset token is local/debug only."""

    message: str
    reset_token: str | None = None


class PasswordResetRequest(BaseModel):
    """Request payload to reset a password using a recovery token."""

    token: str
    new_password: str = Field(..., min_length=6)
