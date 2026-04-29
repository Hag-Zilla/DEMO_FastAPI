"""Report router - Expense reporting and analytics."""

from datetime import datetime
from typing import cast

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from ..core.cache import user_cache_key_builder
from ..core.logging import get_logger
from ..services.report_service import ReportService
from ..utils.dependencies import AdminUserDep, CurrentUserDep, SessionDep

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/monthly/{year}/{month}", name="Monthly Report")
@cache(expire=300, namespace="reports", key_builder=user_cache_key_builder)
async def get_monthly_report(
    year: int,
    month: int,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Get monthly expense report for the authenticated user.

    Args:
        year: Year (e.g., 2026).
        month: Month (1-12).
        db: Database session.
        current_user: Current authenticated user.

    Returns:
        Dict with user info and monthly expense report.

    Raises:
        ValueError: If month is not between 1 and 12.
    """
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    report = ReportService.get_monthly_report(
        db, cast(str, current_user.id), year, month
    )

    logger.info(
        "User %s generated monthly report for %s-%02d", current_user.id, year, month
    )

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "period": f"{year}-{month:02d}",
        "period_type": "monthly",
        **report,
    }


@router.get("/period", name="Period Report")
def get_period_report(
    start_date: datetime,
    end_date: datetime,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Get expense report for a custom date range.

    Args:
        start_date: Start date in ISO format (e.g., 2026-02-01T00:00:00).
        end_date: End date in ISO format (e.g., 2026-02-28T23:59:59).
        db: Database session.
        current_user: Current authenticated user.

    Returns:
        Dict with user info and custom period expense report.

    Raises:
        ValueError: If start_date is not before end_date.
    """
    if start_date >= end_date:
        raise ValueError("start_date must be before end_date")

    report = ReportService.get_custom_period_report(
        db, cast(str, current_user.id), start_date, end_date
    )

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
@cache(expire=120, namespace="reports-all", key_builder=user_cache_key_builder)
async def get_all_reports(
    db: SessionDep,
    _admin: AdminUserDep,
):
    """Get aggregated expense reports for all users (admin only).

    Args:
        db: Database session.
        _admin: Admin user (access already validated by dependency).

    Returns:
        Dict with keys: report_type, total_across_users, total_expenses_count, by_user.
    """
    result = ReportService.get_all_users_report(db)
    logger.info("Admin generated all-users report")
    return result
