"""Analytics router — admin-only business KPI endpoint."""

from fastapi import APIRouter
from sqlalchemy import func

from ..core.enums import UserStatus
from ..core.logging import get_logger
from ..core.metrics import (
    ACTIVE_USERS,
    EXPENSE_CREATED,
    EXPENSE_DELETED,
    LOGIN_SUCCESS,
    LOGIN_FAILURE,
    BUDGET_EXCEEDED,
)
from ..database.models.expense import Expense
from ..database.models.user import User as UserModel
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
            "expense_created_total": EXPENSE_CREATED.total(),
            "expense_deleted_total": EXPENSE_DELETED.total(),
            "login_success_total": LOGIN_SUCCESS.total(),
            "login_failure_total": LOGIN_FAILURE.total(),
            "budget_exceeded_total": BUDGET_EXCEEDED.total(),
        },
        "note": "Counter values reflect the current process lifetime only.",
    }
