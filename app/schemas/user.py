"""User-related Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        json_schema_extra={"example": "john_doe"},
    )
    budget: float = Field(
        default=0.0,
        ge=0,
        description="The user's budget",
        json_schema_extra={"example": 1000.0},
    )


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ...,
        min_length=6,
        description="The user's password",
        json_schema_extra={"example": "secure_password123"},
    )


class UserUpdate(BaseModel):
    """Schema for user updates."""

    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        json_schema_extra={"example": "john_doe_updated"},
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        description="The user's password",
        json_schema_extra={"example": "new_secure_password123"},
    )
    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="The user's budget",
        json_schema_extra={"example": 1200.0},
    )
    role: Optional[UserRole] = Field(
        default=None,
        description="The user's role (admin or user)",
        json_schema_extra={"example": UserRole.USER},
    )
    status: Optional[UserStatus] = Field(
        default=None,
        description="The user's account status (pending, active, or disabled)",
        json_schema_extra={"example": UserStatus.ACTIVE},
    )


class UserSelfUpdate(BaseModel):
    """Schema for self user updates (non-admin fields only)."""

    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="The user's unique username",
        json_schema_extra={"example": "john_doe_updated"},
    )
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        description="The user's password",
        json_schema_extra={"example": "new_secure_password123"},
    )
    budget: Optional[float] = Field(
        default=None,
        ge=0,
        description="The user's budget",
        json_schema_extra={"example": 1200.0},
    )


class UserResponse(UserBase):
    """Schema for user responses (read operations)."""

    id: int
    role: UserRole
    status: UserStatus

    class Config:
        """Pydantic config."""

        from_attributes = True
