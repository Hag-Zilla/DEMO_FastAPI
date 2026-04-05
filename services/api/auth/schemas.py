"""Auth-specific Pydantic schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    """Decoded JWT token payload."""

    username: str | None = None
