"""Custom Prometheus business metrics.

These counters track domain-level events (not just HTTP request counts, which
prometheus-fastapi-instrumentator handles separately).  Increment them from
service or router code to get business-level observability.

Usage::

    from api.core.metrics import EXPENSE_CREATED, LOGIN_SUCCESS, BUDGET_EXCEEDED

    EXPENSE_CREATED.labels(category="food").inc()
    LOGIN_SUCCESS.inc()
    BUDGET_EXCEEDED.inc()
"""

from prometheus_client import Counter, Gauge

# ---------------------------------------------------------------------------
# Business event counters
# ---------------------------------------------------------------------------

EXPENSE_CREATED: Counter = Counter(
    "expense_created_total",
    "Total number of expenses created",
    ["category"],
)

EXPENSE_DELETED: Counter = Counter(
    "expense_deleted_total",
    "Total number of expenses deleted",
)

LOGIN_SUCCESS: Counter = Counter(
    "user_login_success_total",
    "Total number of successful user logins",
)

LOGIN_FAILURE: Counter = Counter(
    "user_login_failure_total",
    "Total number of failed login attempts",
)

BUDGET_EXCEEDED: Counter = Counter(
    "budget_exceeded_total",
    "Total number of times a user's budget was found exceeded during an alert check",
)

# ---------------------------------------------------------------------------
# Informational gauges
# ---------------------------------------------------------------------------

ACTIVE_USERS: Gauge = Gauge(
    "active_users_total",
    "Number of users with ACTIVE status (snapshot, updated on /analytics calls)",
)
