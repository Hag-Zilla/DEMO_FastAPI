"""Expense-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import ExpenseCategory


class ExpenseBase(BaseModel):
    """Base expense schema."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Description of the expense",
        json_schema_extra={"example": "Lunch at restaurant"},
    )
    amount: float = Field(
        ..., gt=0, description="Expense amount", json_schema_extra={"example": 25.50}
    )
    category: ExpenseCategory = Field(
        ...,
        description="Expense category",
        json_schema_extra={"example": ExpenseCategory.FOOD},
    )


class ExpenseCreate(ExpenseBase):
    """Schema for expense creation."""


class ExpenseUpdate(BaseModel):
    """Schema for expense updates."""

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Description of the expense",
        json_schema_extra={"example": "Lunch at restaurant"},
    )
    amount: Optional[float] = Field(
        default=None,
        gt=0,
        description="Expense amount",
        json_schema_extra={"example": 30.00},
    )
    category: Optional[ExpenseCategory] = Field(
        default=None,
        description="Expense category",
        json_schema_extra={"example": ExpenseCategory.FOOD},
    )


class ExpenseResponse(ExpenseBase):
    """Schema for expense responses (read operations)."""

    id: int
    date: datetime
    user_id: int

    class Config:
        """Pydantic config."""

        from_attributes = True
