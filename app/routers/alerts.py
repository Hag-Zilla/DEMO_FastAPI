"""Alert router - Budget overflow detection."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..core.security import get_current_user
from ..database.models.expense import Expense as ExpenseModel
from ..database.models.user import User as UserModel
from ..database.session import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", name="Check Budget Alerts")
async def check_alerts(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Check for budget overruns in current month.

    Returns:
    - total_spent: Total expenses for the current month
    - budget: User's monthly budget limit
    - status: "ok" (within budget) or "exceeded" (over budget)
    - remaining: Budget remaining (or overage amount)
    - percentage: Percentage of budget used
    - expenses_by_category: Breakdown by category
    """
    # Get current month
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_next_month = (
        datetime(now.year, now.month + 1, 1)
        if now.month < 12
        else datetime(now.year + 1, 1, 1)
    )

    # Query total expenses for current month
    total_spent_query = (
        db.query(func.sum(ExpenseModel.amount))  # pylint: disable=not-callable
        .filter(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.date >= start_of_month,
            ExpenseModel.date < start_of_next_month,
        )
        .scalar()
    )

    total_spent = float(total_spent_query) if total_spent_query else 0.0

    # Query expenses by category for current month
    category_breakdown = (
        db.query(  # type: ignore[call-overload]
            ExpenseModel.category,
            func.count(ExpenseModel.id).label("count"),  # pylint: disable=not-callable
            func.sum(ExpenseModel.amount).label("total"),  # pylint: disable=not-callable
        )
        .filter(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.date >= start_of_month,
            ExpenseModel.date < start_of_next_month,
        )
        .group_by(ExpenseModel.category)
        .all()
    )

    # Build category breakdown
    expenses_by_category = {
        row.category.value: {
            "count": row.count,
            "total": float(row.total) if row.total else 0.0,  # type: ignore[arg-type]
        }
        for row in category_breakdown
    }

    # Calculate budget status
    budget = float(current_user.budget)
    remaining = budget - total_spent
    percentage: float = (total_spent / budget * 100) if budget > 0 else 0.0

    # Determine status
    if total_spent > budget:
        status = "exceeded"
        logger.warning(
            "User %s exceeded budget: spent %s, budget %s",
            current_user.id,
            total_spent,
            budget,
        )
    else:
        status = "ok"

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "month": f"{now.year}-{now.month:02d}",
        "total_spent": total_spent,
        "budget": budget,
        "remaining": remaining,
        "percentage_used": round(percentage, 2),
        "status": status,
        "expenses_by_category": expenses_by_category,
    }
