"""User-related Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        example="john_doe",
    )
    budget: float = Field(
        default=0.0,
        ge=0,
        description="The user's budget",
        example=1000.0,
    )


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ...,
        min_length=6,
        description="The user's password",
        example="secure_password123",
    )


class UserUpdate(BaseModel):
    """Schema for user updates."""

    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        example="john_doe_updated",
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        description="The user's password",
        example="new_secure_password123",
    )
    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="The user's budget",
        example=1200.0,
    )
    role: Optional[UserRole] = Field(
        default=None,
        description="The user's role (admin or user)",
        example=UserRole.USER,
    )
    disabled: Optional[bool] = Field(
        default=None,
        description="Whether the user is disabled",
        example=False,
    )


class UserResponse(UserBase):
    """Schema for user responses (read operations)."""

    id: int
    role: UserRole
    disabled: bool

    class Config:
        """Pydantic config."""

        from_attributes = True
