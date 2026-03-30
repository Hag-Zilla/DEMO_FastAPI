"""Expense database model."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from ..session import Base
from app.core.enums import ExpenseCategory


class Expense(Base):
    """Expense model for storing user expense records."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    category: ExpenseCategory = Column(Enum(ExpenseCategory))  # type: ignore[assignment]
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")
