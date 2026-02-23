"""Report router - Expense reporting and analytics."""

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
from ..utils.dependencies import get_admin_user

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _build_expense_report(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    """Helper function to build expense report for a user within a date range."""
    # Get total expenses
    total_query = (
        db.query(func.sum(ExpenseModel.amount))  # pylint: disable=not-callable
        .filter(
            ExpenseModel.user_id == user_id,
            ExpenseModel.date >= start_date,
            ExpenseModel.date < end_date,
        )
        .scalar()
    )
    total = float(total_query) if total_query else 0.0

    # Get count of expenses
    count_query = (
        db.query(func.count(ExpenseModel.id))  # pylint: disable=not-callable
        .filter(
            ExpenseModel.user_id == user_id,
            ExpenseModel.date >= start_date,
            ExpenseModel.date < end_date,
        )
        .scalar()
    )
    count = count_query or 0

    # Get breakdown by category
    category_breakdown = (
        db.query(
            ExpenseModel.category,
            func.count(ExpenseModel.id).label("count"),  # pylint: disable=not-callable
            func.sum(ExpenseModel.amount).label("total"),  # pylint: disable=not-callable
        )
        .filter(
            ExpenseModel.user_id == user_id,
            ExpenseModel.date >= start_date,
            ExpenseModel.date < end_date,
        )
        .group_by(ExpenseModel.category)
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


@router.get("/monthly/{year}/{month}", name="Monthly Report")
async def get_monthly_report(
    year: int,
    month: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Get monthly expense report for the authenticated user.

    Args:
        year: Year (e.g., 2026)
        month: Month (1-12)
    """
    # Validate month
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    # Get date range for the month
    start_date = datetime(year, month, 1)
    end_date = (
        datetime(year, month + 1, 1)
        if month < 12
        else datetime(year + 1, 1, 1)
    )

    report = _build_expense_report(db, current_user.id, start_date, end_date)

    logger.info("User %s generated monthly report for %s-%02d", current_user.id, year, month)

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "period": f"{year}-{month:02d}",
        "period_type": "monthly",
        **report,
    }


@router.get("/period", name="Period Report")
async def get_period_report(
    start_date: datetime,
    end_date: datetime,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    """Get expense report for a custom date range.

    Query parameters:
    - start_date: Start date (ISO format: 2026-02-01T00:00:00)
    - end_date: End date (ISO format: 2026-02-28T23:59:59)
    """
    if start_date >= end_date:
        raise ValueError("start_date must be before end_date")

    report = _build_expense_report(db, current_user.id, start_date, end_date)

    logger.info(
        "User %s generated period report from %s to %s",
        current_user.id,
        start_date.date(),
        end_date.date(),
    )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "period": f"{start_date.date()} to {end_date.date()}",
        "period_type": "custom",
        **report,
    }


@router.get("/all", name="Admin All Reports")
async def get_all_reports(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Get aggregated expense reports for all users (admin only).

    Returns:
    - total_across_users: Total expenses across all users
    - user_count: Number of users with expenses
    - by_user: Breakdown by user
    """
    # Total across all users
    total_query = db.query(func.sum(ExpenseModel.amount)).scalar()  # pylint: disable=not-callable
    total = float(total_query) if total_query else 0.0

    # Count total expenses
    count_query = db.query(func.count(ExpenseModel.id)).scalar()  # pylint: disable=not-callable
    count = count_query or 0

    # Get report by user
    user_reports = {}
    users_with_expenses = (
        db.query(ExpenseModel.user_id)
        .distinct()
        .all()
    )

    for (user_id,) in users_with_expenses:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            # Build report for this user
            total_user_query = (
                db.query(func.sum(ExpenseModel.amount))  # pylint: disable=not-callable
                .filter(ExpenseModel.user_id == user_id)
                .scalar()
            )
            user_total = float(total_user_query) if total_user_query else 0.0

            count_user_query = (
                db.query(func.count(ExpenseModel.id))  # pylint: disable=not-callable
                .filter(ExpenseModel.user_id == user_id)
                .scalar()
            )
            user_count = count_user_query or 0

            user_reports[user.username] = {
                "user_id": user_id,
                "total_expenses": user_total,
                "count": user_count,
                "average": round(user_total / user_count, 2) if user_count > 0 else 0.0,
            }

    logger.info("Admin generated all-users report")

    return {
        "report_type": "admin_all_users",
        "total_across_users": total,
        "total_expenses_count": count,
        "by_user": user_reports,
    }
