"""Analytics service — encapsulates KPI aggregation logic."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from services.api.core.enums import UserStatus
from services.api.core.logging import get_logger
from services.api.core.metrics import (
    ACTIVE_USERS,
    BUDGET_EXCEEDED,
    EXPENSE_CREATED,
    EXPENSE_DELETED,
    LOGIN_FAILURE,
    LOGIN_SUCCESS,
)
from services.api.database.models.expense import Expense
from services.api.database.models.user import User

logger = get_logger(__name__)


class AnalyticsService:
    """Service providing business KPI aggregation over the live database."""

    @staticmethod
    def get_summary(db: Session) -> dict:
        """Return a KPI snapshot combining live DB counts and process-lifetime counters.

        Also updates the ACTIVE_USERS Prometheus gauge to mirror the DB state.

        Args:
            db: Database session.

        Returns:
            Dict with ``database`` and ``counters`` sub-dicts.
        """
        total_users: int = db.query(func.count(User.id)).scalar() or 0  # pylint: disable=not-callable
        active_users: int = (
            db.query(func.count(User.id))  # pylint: disable=not-callable
            .filter(User.status == UserStatus.ACTIVE)  # type: ignore[arg-type]
            .scalar()
            or 0
        )
        total_expenses: int = db.query(func.count(Expense.id)).scalar() or 0  # pylint: disable=not-callable
        total_spent: float = float(
            db.query(func.sum(Expense.amount)).scalar() or 0  # pylint: disable=not-callable
        )

        ACTIVE_USERS.set(active_users)
        logger.info(
            "Analytics summary computed: %d active users, %d expenses",
            active_users,
            total_expenses,
        )

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
