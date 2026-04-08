"""Analytics router — admin-only business KPI endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from prometheus_client import REGISTRY
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.enums import UserStatus
from ..core.logging import get_logger
from ..core.metrics import ACTIVE_USERS
from ..database.models.expense import Expense
from ..database.models.user import User as UserModel
from ..database.session import get_db
from ..utils.dependencies import get_admin_user

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _prometheus_counter_total(metric_name: str) -> float:
    """Read the current total from a registered Prometheus counter by name."""
    total = 0.0
    for metric in REGISTRY.collect():
        if metric.name == metric_name:
            for sample in metric.samples:
                if sample.name in (metric_name, metric_name + "_total"):
                    total += sample.value
    return total


@router.get("/", name="Business Analytics Summary")
def get_analytics_summary(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(get_admin_user)],
):
    """Return a snapshot of key business metrics (admin only).

    Includes live database counts and the current values of the in-process
    Prometheus counters.  Counter values reset when the process restarts;
    for persistence use the ``/metrics`` Prometheus endpoint with a remote
    write target.
    """
    # ---- Live database counts ----
    total_users: int = db.query(func.count(UserModel.id)).scalar() or 0  # pylint: disable=not-callable
    active_users: int = (
        db.query(func.count(UserModel.id))  # pylint: disable=not-callable
        .filter(UserModel.status == UserStatus.ACTIVE)  # type: ignore[arg-type]
        .scalar()
        or 0
    )
    total_expenses: int = db.query(func.count(Expense.id)).scalar() or 0  # pylint: disable=not-callable
    total_spent: float = float(
        db.query(func.sum(Expense.amount)).scalar() or 0  # pylint: disable=not-callable
    )

    # Update the gauge so Prometheus also reflects real DB state
    ACTIVE_USERS.set(active_users)

    return {
        "database": {
            "total_users": total_users,
            "active_users": active_users,
            "total_expenses": total_expenses,
            "total_amount_tracked": round(total_spent, 2),
        },
        "counters": {
            "expense_created_total": _prometheus_counter_total("expense_created"),
            "expense_deleted_total": _prometheus_counter_total("expense_deleted"),
            "login_success_total": _prometheus_counter_total("user_login_success"),
            "login_failure_total": _prometheus_counter_total("user_login_failure"),
            "budget_exceeded_total": _prometheus_counter_total("budget_exceeded"),
        },
        "note": (
            "Counter values reflect the current process lifetime only. "
            "Scrape /metrics for persistent Prometheus time-series data."
        ),
    }
