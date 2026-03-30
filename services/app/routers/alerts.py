"""Alert router - Budget overflow detection."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..core.security import get_current_user
from ..database.models.user import User as UserModel
from ..database.session import get_db
from ..services.alert_service import AlertService

logger = get_logger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", name="Check Budget Alerts")
def check_alerts(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
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
