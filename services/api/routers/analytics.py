"""Analytics router — admin-only business KPI endpoint."""

from fastapi import APIRouter

from ..core.logging import get_logger
from ..services.analytics_service import AnalyticsService
from ..utils.dependencies import AdminUserDep, SessionDep

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", name="Business Analytics Summary")
def get_analytics_summary(
    db: SessionDep,
    _admin: AdminUserDep,
):
    """Return a snapshot of key business metrics (admin only).

    Includes live database counts and in-process business counters.
    Counter values reset when the process restarts.
    """
    return AnalyticsService.get_summary(db)
