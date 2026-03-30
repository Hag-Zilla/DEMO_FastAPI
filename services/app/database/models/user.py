"""User database model."""

from sqlalchemy import Column, Integer, String, Numeric, Enum
from sqlalchemy.orm import relationship

from ..session import Base
from app.core.enums import UserRole, UserStatus


class User(Base):
    """User model for storing user information and credentials."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    budget = Column(Numeric(precision=12, scale=2))
    role: UserRole = Column(Enum(UserRole), default=UserRole.USER)  # type: ignore[assignment]
    status: UserStatus = Column(  # type: ignore[assignment]
        Enum(UserStatus), default=UserStatus.PENDING
    )  # PENDING, ACTIVE, or DISABLED
    expenses = relationship("Expense", back_populates="owner")
