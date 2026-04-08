r"""Locust load test - simulates realistic user journeys against the API.

Usage (against a running dev server)::

    # Start the API first:
    make run

    # Then run Locust (from repo root):
    locust -f services/api/tests/load_tests/locustfile.py --host http://localhost:8000

    # Or use the Makefile (recommended):
    make load-test

    # Headless (CI) mode — 20 users, 5 spawn/s, 60 s duration:
    make load-test-headless

See: https://docs.locust.io/
"""

import random
import string

from locust import HttpUser, between, task


def _random_suffix(n: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class RegularUser(HttpUser):
    """Simulates a regular authenticated user interacting with the expense API."""

    wait_time = between(0.5, 2.0)

    # ----------------------------------------------------------------
    # Auth (runs once at user "spawn")
    # ----------------------------------------------------------------

    def on_start(self) -> None:
        """Register a unique user and obtain a JWT for subsequent requests."""
        suffix = _random_suffix()
        self.username = f"loadtest_{suffix}"
        self.password = "LoadTest@1234!"  # pragma: allowlist secret

        # Register
        self.client.post(
            "/api/v1/users/create",
            json={
                "username": self.username,
                "password": self.password,
                "budget": 2000.0,
            },
        )

        # Login
        resp = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
            },
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            # Mark as non-authenticated so tasks fail gracefully
            self.client.headers.pop("Authorization", None)

    # ----------------------------------------------------------------
    # Tasks
    # ----------------------------------------------------------------

    @task(3)
    def list_expenses(self) -> None:
        """Browse expense list (most common read operation)."""
        self.client.get("/api/v1/expenses/", name="/api/v1/expenses/ [list]")

    @task(2)
    def create_expense(self) -> None:
        """Create a new expense."""
        categories = ["food", "transport", "entertainment", "health", "utilities"]
        self.client.post(
            "/api/v1/expenses/",
            json={
                "description": f"Load test expense {_random_suffix()}",
                "amount": round(random.uniform(5.0, 200.0), 2),
                "category": random.choice(categories),
            },
            name="/api/v1/expenses/ [create]",
        )

    @task(1)
    def check_alerts(self) -> None:
        """Check budget alerts (cached, should be fast)."""
        self.client.get("/api/v1/alerts/", name="/api/v1/alerts/")

    @task(1)
    def monthly_report(self) -> None:
        """Fetch a monthly report (cached)."""
        self.client.get(
            "/api/v1/reports/monthly/2025/1",
            name="/api/v1/reports/monthly/{year}/{month}",
        )

    @task(1)
    def period_report(self) -> None:
        """Fetch a custom period report."""
        self.client.get(
            "/api/v1/reports/period",
            params={
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T23:59:59",
            },
            name="/api/v1/reports/period",
        )

    @task(1)
    def health_check(self) -> None:
        """Liveness probe (fast, no auth required)."""
        self.client.get("/health/live", name="/health/live")


class AdminUser(HttpUser):
    """Simulates an admin user performing management and reporting operations."""

    wait_time = between(1.0, 5.0)
    weight = 1  # 1 admin for every 10 regular users

    def on_start(self) -> None:
        """Log in as admin (must exist in the target environment)."""
        resp = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": "admin",
                "password": "AdminSecret@1234!",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(2)
    def all_users_report(self) -> None:
        """Admin all-users report (cached)."""
        self.client.get("/api/v1/reports/all", name="/api/v1/reports/all")

    @task(1)
    def analytics(self) -> None:
        """Business analytics summary."""
        self.client.get("/api/v1/analytics/", name="/api/v1/analytics/")
