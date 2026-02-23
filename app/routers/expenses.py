"""Expense management router."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.enums import ExpenseCategory
from ..core.exceptions import ResourceNotFoundException
from ..core.logging import get_logger
from ..core.security import get_current_user
from ..database.models.expense import Expense as ExpenseModel
from ..database.models.user import User as UserModel
from ..database.session import get_db
from ..schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate

logger = get_logger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", name="List Expenses", response_model=list[ExpenseResponse])
async def list_expenses(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    category: Optional[ExpenseCategory] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """List all expenses for the authenticated user.

    Optional filters:
    - category: Filter by expense category
    - start_date: Filter expenses on or after this date
    - end_date: Filter expenses on or before this date
    """
    query = db.query(ExpenseModel).filter(ExpenseModel.user_id == current_user.id)

    if category:
        query = query.filter(ExpenseModel.category == category)
    if start_date:
        query = query.filter(ExpenseModel.date >= start_date)
    if end_date:
        query = query.filter(ExpenseModel.date <= end_date)

    expenses = query.order_by(ExpenseModel.date.desc()).all()
    logger.info("User %s listed %s expenses", current_user.id, len(expenses))
    return expenses


@router.post(
    "/",
    name="Create Expense",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    expense: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Create a new expense for the authenticated user."""
    db_expense = ExpenseModel(
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
        user_id=current_user.id,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    logger.info(
        "User %s created expense %s: %s (%s)",
        current_user.id,
        db_expense.id,
        expense.description,
        expense.amount,
    )
    return db_expense


@router.get("/{expense_id}", name="Get Expense", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Get a specific expense by ID (must be owner)."""
    expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()

    if not expense:
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    # Verify ownership (non-admin users can only see their own expenses)
    if current_user.role.value != "admin" and expense.user_id != current_user.id:
        logger.warning(
            "User %s attempted to access expense %s owned by %s",
            current_user.id,
            expense_id,
            expense.user_id,
        )
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    return expense


@router.put("/{expense_id}", name="Update Expense", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Update an expense (must be owner or admin)."""
    expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()

    if not expense:
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    # Verify ownership
    if current_user.role.value != "admin" and expense.user_id != current_user.id:
        logger.warning(
            "User %s attempted to update expense %s owned by %s",
            current_user.id,
            expense_id,
            expense.user_id,
        )
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    # Update only provided fields
    if expense_update.description is not None:
        expense.description = expense_update.description
    if expense_update.amount is not None:
        expense.amount = expense_update.amount
    if expense_update.category is not None:
        expense.category = expense_update.category

    db.commit()
    db.refresh(expense)
    logger.info("User %s updated expense %s", current_user.id, expense_id)
    return expense


@router.delete("/{expense_id}", name="Delete Expense", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Delete an expense (must be owner or admin)."""
    expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()

    if not expense:
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    # Verify ownership
    if current_user.role.value != "admin" and expense.user_id != current_user.id:
        logger.warning(
            "User %s attempted to delete expense %s owned by %s",
            current_user.id,
            expense_id,
            expense.user_id,
        )
        raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

    db.delete(expense)
    db.commit()
    logger.info("User %s deleted expense %s", current_user.id, expense_id)
