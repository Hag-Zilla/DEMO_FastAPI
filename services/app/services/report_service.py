"""Report service encapsulating reporting and analytics logic."""

from datetime import datetime
from typing import Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.models.expense import Expense

logger = get_logger(__name__)


class ReportService:
    """Service handling expense reporting, analytics, and data aggregation."""

    @staticmethod
    def build_expense_report(
        db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Build an expense report for a user within a date range.

        Args:
            db: Database session
            user_id: ID of the user
            start_date: Start date for the report period
            end_date: End date for the report period

        Returns:
            Dict containing:
            - total_expenses: Total amount spent
            - count: Number of expenses
            - average: Average expense amount
            - by_category: Breakdown by expense category
        """
        # Get total expenses
        total_query = (
            db.query(func.sum(Expense.amount))  # pylint: disable=not-callable
            .filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .scalar()
        )
        total = float(total_query) if total_query else 0.0

        # Get count of expenses
        count_query = (
            db.query(func.count(Expense.id))  # pylint: disable=not-callable
            .filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .scalar()
        )
        count = count_query or 0

        # Get breakdown by category
        category_breakdown = (
            db.query(  # type: ignore[call-overload]
                Expense.category,
                func.count(Expense.id).label("count"),  # pylint: disable=not-callable
                func.sum(Expense.amount).label("total"),  # pylint: disable=not-callable
            )
            .filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .group_by(Expense.category)
            .all()
        )

        by_category = {
            row.category.value: {
                "count": row.count,
                "total": float(row.total) if row.total else 0.0,
            }
            for row in category_breakdown
        }

        return {
            "total_expenses": total,
            "count": count,
            "average": round(total / count, 2) if count > 0 else 0.0,
            "by_category": by_category,
        }

    @staticmethod
    def get_monthly_report(
        db: Session, user_id: int, year: int, month: int
    ) -> Dict[str, Any]:
        """
        Get monthly expense report for a user.

        Args:
            db: Database session
            user_id: User ID
            year: Report year
            month: Report month (1-12)

        Returns:
            Report dict from build_expense_report
        """
        start_date = datetime(year, month, 1)
        # Calculate end of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return ReportService.build_expense_report(db, user_id, start_date, end_date)

    @staticmethod
    def get_custom_period_report(
        db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get expense report for a custom date period.

        Args:
            db: Database session
            user_id: User ID
            start_date: Period start date
            end_date: Period end date

        Returns:
            Report dict from build_expense_report
        """
        return ReportService.build_expense_report(db, user_id, start_date, end_date)

    @staticmethod
    def get_all_users_stats(db: Session) -> Dict[str, Any]:
        """
        Get aggregate statistics across all users (admin only).

        Args:
            db: Database session

        Returns:
            Dict with total_users, total_expenses, average_per_user, etc.
        """
        from app.database.models.user import User

        # Total users
        total_users = db.query(func.count(User.id)).scalar() or 0  # pylint: disable=not-callable

        # Total expenses
        total_expenses_query = db.query(func.sum(Expense.amount)).scalar()  # pylint: disable=not-callable
        total_expenses = float(total_expenses_query) if total_expenses_query else 0.0

        # Average per user
        average_per_user = (
            round(total_expenses / total_users, 2) if total_users > 0 else 0.0
        )

        # Number of expenses
        total_expense_count = (
            db.query(func.count(Expense.id)).scalar() or 0  # pylint: disable=not-callable
        )

        return {
            "total_users": total_users,
            "total_expenses": total_expenses,
            "total_expense_count": total_expense_count,
            "average_per_user": average_per_user,
        }
