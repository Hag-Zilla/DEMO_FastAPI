"""Expense database model."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from ..session import Base
from services.api.core.enums import ExpenseCategory


class Expense(Base):
    """Expense model for storing user expense records."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Numeric(precision=12, scale=2))
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    category: ExpenseCategory = Column(Enum(ExpenseCategory))  # type: ignore[assignment]
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")
