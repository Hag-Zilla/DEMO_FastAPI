"""User database model."""

from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
from sqlalchemy.orm import relationship

from ..session import Base
from app.core.enums import UserRole


class User(Base):
    """User model for storing user information and credentials."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    budget = Column(Float)
    role = Column(Enum(UserRole), default=UserRole.USER)
    disabled = Column(Boolean, default=False)  # Indicates if the user account is disabled
    expenses = relationship("Expense", back_populates="owner")
