"""Expense management router."""

from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session

from ..core.enums import ExpenseCategory
from ..core.logging import get_logger
from ..core.security import get_current_user
from ..database.models.user import User as UserModel
from ..database.session import get_db
from ..schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from ..services.expense_service import ExpenseService

logger = get_logger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", name="List Expenses", response_model=list[ExpenseResponse])
def list_expenses(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    category: Optional[ExpenseCategory] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of results"
    ),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
):
    """List expenses for the authenticated user with optional filters and pagination.

    Admins see all expenses; regular users only their own.
    """
    return ExpenseService.list_expenses_for_user(
        db,
        cast(int, current_user.id),
        current_user.role,
        category,
        start_date,
        end_date,
        limit,
        offset,
    )


@router.post(
    "/",
    name="Create Expense",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense: ExpenseCreate = Body(
        ...,
        example={
            "description": "Lunch at restaurant",
            "amount": 25.5,
            "category": "food",
        },
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new expense for the authenticated user.

    Valid categories: food, transportation, entertainment, utilities,
    healthcare, education, shopping, other
    """
    return ExpenseService.create_expense(db, cast(int, current_user.id), expense)


@router.get("/{expense_id}", name="Get Expense", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get a specific expense by ID (must be owner or admin)."""
    return ExpenseService.verify_expense_access(
        db, expense_id, cast(int, current_user.id), current_user.role
    )


@router.put("/{expense_id}", name="Update Expense", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update an expense (must be owner or admin)."""
    return ExpenseService.update_expense(
        db, expense_id, cast(int, current_user.id), current_user.role, expense_update
    )


@router.delete(
    "/{expense_id}", name="Delete Expense", status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete an expense (must be owner or admin)."""
    ExpenseService.delete_expense(
        db, expense_id, cast(int, current_user.id), current_user.role
    )
