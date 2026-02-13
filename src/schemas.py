from typing import Optional
from pydantic import BaseModel, Field

# User-related schemas
class UserSchema(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        example="john_doe"
    )
    password: str = Field(
        ...,
        min_length=3,
        description="The user's password",
        example="secure_password123"
    )
    budget: float = Field(
        ...,
        ge=0,
        description="The user's budget",
        example=1000.0
    )
    # role and disabled removed from creation schema

class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        example="john_doe_updated"
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        description="The user's password",
        example="new_secure_password123"
    )
    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="The user's budget",
        example=1200.0
    )
    role: Optional[str] = Field(
        default=None,
        description="The user's role (admin or user)",
        example="user"
    )
    disabled: Optional[bool] = Field(
        default=None,
        description="Whether the user is disabled",
        example=False
    )

# Token-related schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = {"from_attributes": True}
