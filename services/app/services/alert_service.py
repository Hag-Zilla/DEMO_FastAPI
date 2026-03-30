"""Alert service encapsulating budget monitoring and threshold logic."""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.models.expense import Expense
from app.database.models.user import User

logger = get_logger(__name__)


class AlertService:
    """Service handling budget alert checking and threshold monitoring."""

    @staticmethod
    def check_budget_alerts(db: Session, user: User) -> Dict[str, Any]:
        """
        Check for budget overruns in current month.

        Args:
            db: Database session
            user: User model instance

        Returns:
            Dict with budget status including:
            - total_spent: Total expenses for the current month
            - budget: User's monthly budget limit
            - status: "ok" (within budget) or "exceeded" (over budget)
            - remaining: Budget remaining (or overage amount)
            - percentage: Percentage of budget used
            - expenses_by_category: Breakdown by category
        """
        # Get current month boundaries
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        start_of_next_month = (
            datetime(now.year, now.month + 1, 1)
            if now.month < 12
            else datetime(now.year + 1, 1, 1)
        )

        # Query total expenses for current month
        total_spent_query = (
            db.query(func.sum(Expense.amount))  # pylint: disable=not-callable
            .filter(
                Expense.user_id == user.id,
                Expense.date >= start_of_month,
                Expense.date < start_of_next_month,
            )
            .scalar()
        )

        total_spent = float(total_spent_query) if total_spent_query else 0.0

        # Query expenses by category for current month
        category_breakdown = (
            db.query(  # type: ignore[call-overload]
                Expense.category,
                func.count(Expense.id).label("count"),  # pylint: disable=not-callable
                func.sum(Expense.amount).label("total"),  # pylint: disable=not-callable
            )
            .filter(
                Expense.user_id == user.id,
                Expense.date >= start_of_month,
                Expense.date < start_of_next_month,
            )
            .group_by(Expense.category)
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
        budget = float(user.budget)
        remaining = budget - total_spent
        percentage: float = (total_spent / budget * 100) if budget > 0 else 0.0

        # Determine status
        if total_spent > budget:
            status = "exceeded"
            logger.warning(
                "User %s exceeded budget: spent %s, budget %s",
                user.id,
                total_spent,
                budget,
            )
        else:
            status = "ok"

        return {
            "total_spent": total_spent,
            "budget": budget,
            "status": status,
            "remaining": abs(remaining),
            "percentage": round(percentage, 2),
            "expenses_by_category": expenses_by_category,
        }

    @staticmethod
    def get_month_spending(
        db: Session,
        user_id: int,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> float:
        """
        Get total spending for a specific month.

        Args:
            db: Database session
            user_id: User ID
            year: Year (defaults to current)
            month: Month (defaults to current)

        Returns:
            Total amount spent in that month
        """
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month

        start_of_month = datetime(year, month, 1)
        start_of_next_month = (
            datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        )

        total = (
            db.query(func.sum(Expense.amount))  # pylint: disable=not-callable
            .filter(
                Expense.user_id == user_id,
                Expense.date >= start_of_month,
                Expense.date < start_of_next_month,
            )
            .scalar()
        )

        return float(total) if total else 0.0

    @staticmethod
    def is_budget_exceeded(db: Session, user: User) -> bool:
        """
        Quick check if user has exceeded budget this month.

        Args:
            db: Database session
            user: User model instance

        Returns:
            True if spending exceeds budget, False otherwise
        """
        total_spent = AlertService.get_month_spending(db, user.id)  # type: ignore[arg-type]
        return total_spent > user.budget  # type: ignore[return-value]
