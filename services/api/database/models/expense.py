"""Expense database model."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from services.api.core.enums import ExpenseCategory
from ..base import Base


class Expense(Base):
    """Expense model for storing user expense records."""

    __tablename__ = "expenses"

    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    description = Column(String)
    amount = Column(Numeric(precision=12, scale=2))
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    category: ExpenseCategory = Column(Enum(ExpenseCategory))  # type: ignore[assignment]
    user_id = Column(String(36), ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")
