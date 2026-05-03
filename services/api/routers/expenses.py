"""Expense management router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Query, status

from ..core.enums import ExpenseCategory
from ..core.logging import get_logger
from ..schemas.common import ListResponse
from ..schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from ..services.expense_service import ExpenseService
from ..utils.dependencies import CurrentUserDep, SessionDep
from ..utils.pagination import make_list_response

logger = get_logger(__name__)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", name="List Expenses", response_model=ListResponse[ExpenseResponse])
def list_expenses(
    db: SessionDep,
    current_user: CurrentUserDep,
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
    expenses = ExpenseService.list_expenses_for_user(
        db,
        current_user.id,
        current_user.role,
        category,
        start_date,
        end_date,
        limit,
        offset,
    )
    total = ExpenseService.count_expenses_for_user(
        db,
        current_user.id,
        current_user.role,
        category,
        start_date,
        end_date,
    )
    return make_list_response(expenses, total)


@router.post(
    "/",
    name="Create Expense",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    db: SessionDep,
    current_user: CurrentUserDep,
    expense: ExpenseCreate = Body(
        ...,
        example={
            "description": "Lunch at restaurant",
            "amount": 25.5,
            "category": "food",
        },
    ),
):
    """Create a new expense for the authenticated user.

    Valid categories: food, transportation, entertainment, utilities,
    healthcare, education, shopping, other
    """
    return ExpenseService.create_expense(db, current_user.id, expense)


@router.get("/{expense_id}", name="Get Expense", response_model=ExpenseResponse)
def get_expense(
    expense_id: str,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Get a specific expense by ID (must be owner or admin)."""
    return ExpenseService.verify_expense_access(
        db, expense_id, current_user.id, current_user.role
    )


@router.put("/{expense_id}", name="Update Expense", response_model=ExpenseResponse)
def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Update an expense (must be owner or admin)."""
    return ExpenseService.update_expense(
        db, expense_id, current_user.id, current_user.role, expense_update
    )


@router.delete(
    "/{expense_id}", name="Delete Expense", status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense(
    expense_id: str,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Delete an expense (must be owner or admin)."""
    ExpenseService.delete_expense(db, expense_id, current_user.id, current_user.role)
