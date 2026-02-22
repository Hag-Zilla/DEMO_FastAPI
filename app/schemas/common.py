"""Common/shared Pydantic schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str

    model_config = {"from_attributes": True}
