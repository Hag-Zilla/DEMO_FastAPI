"""Alert router - Budget overflow detection."""

from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from ..core.cache import user_cache_key_builder
from ..core.logging import get_logger
from ..services.alert_service import AlertService
from ..utils.dependencies import CurrentUserDep, SessionDep

logger = get_logger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", name="Check Budget Alerts")
@cache(expire=60, namespace="alerts", key_builder=user_cache_key_builder)
async def check_alerts(
    db: SessionDep,
    current_user: CurrentUserDep,
):
    """Check for budget overruns in current month.

    Returns:
    - total_spent: Total expenses for the current month
    - budget: User's monthly budget limit
    - status: "ok" (within budget) or "exceeded" (over budget)
    - remaining: Budget remaining (negative when exceeded)
    - percentage_used: Percentage of budget used
    - expenses_by_category: Breakdown by category
    """
    now = datetime.now(timezone.utc)
    result = AlertService.check_budget_alerts(db, current_user)
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "month": f"{now.year}-{now.month:02d}",
        **result,
    }
