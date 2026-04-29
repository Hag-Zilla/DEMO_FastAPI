"""User database model."""

import uuid

from sqlalchemy import Column, String, Numeric, Enum
from sqlalchemy.orm import relationship

from services.api.core.enums import UserRole, UserStatus
from ..base import Base


class User(Base):
    """User model for storing user information and credentials."""

    __tablename__ = "users"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    budget = Column(Numeric(precision=12, scale=2))
    role: UserRole = Column(Enum(UserRole), default=UserRole.USER)  # type: ignore[assignment]
    status: UserStatus = Column(  # type: ignore[assignment]
        Enum(UserStatus), default=UserStatus.PENDING
    )  # PENDING, ACTIVE, or DISABLED
    expenses = relationship("Expense", back_populates="owner")
