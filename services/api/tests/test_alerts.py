"""Budget alert endpoint tests."""

import pytest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.core.enums import ExpenseCategory, UserRole, UserStatus
from api.core.security import get_password_hash
from api.database.models.expense import Expense
from api.database.models.user import User


class TestBudgetAlerts:
    """Test cases for GET /alerts/ endpoint."""

    def test_alerts_no_expenses(self, authenticated_client: TestClient) -> None:
        """With no expenses, status is 'ok' and total_spent is 0."""
        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["total_spent"] == 0.0
        assert data["expenses_by_category"] == {}

    def test_alerts_within_budget(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Spending below budget: status 'ok', positive remaining."""
        db.add(
            Expense(
                description="Within budget",
                amount=100.0,
                category=ExpenseCategory.FOOD,
                user_id=test_user.id,
                date=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["total_spent"] == pytest.approx(100.0)
        assert data["remaining"] == pytest.approx(900.0)  # budget=1000 − 100

    def test_alerts_budget_exceeded(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Spending over budget: status 'exceeded' and remaining is negative."""
        db.add(
            Expense(
                description="Over budget",
                amount=1500.0,
                category=ExpenseCategory.SHOPPING,
                user_id=test_user.id,
                date=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "exceeded"
        assert data["total_spent"] == pytest.approx(1500.0)
        assert data["remaining"] < 0  # negative when exceeded

    def test_alerts_percentage_used(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """percentage_used is calculated correctly (50% of 1000 budget)."""
        db.add(
            Expense(
                description="Half budget",
                amount=500.0,
                category=ExpenseCategory.UTILITIES,
                user_id=test_user.id,
                date=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        assert response.json()["percentage_used"] == pytest.approx(50.0)

    def test_alerts_category_breakdown(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Category breakdown correctly groups and sums by category."""
        db.add_all(
            [
                Expense(
                    description="food1",
                    amount=50.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime.now(timezone.utc),
                ),
                Expense(
                    description="food2",
                    amount=30.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime.now(timezone.utc),
                ),
                Expense(
                    description="transport",
                    amount=20.0,
                    category=ExpenseCategory.TRANSPORTATION,
                    user_id=test_user.id,
                    date=datetime.now(timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        categories = response.json()["expenses_by_category"]
        assert "food" in categories
        assert categories["food"]["count"] == 2
        assert categories["food"]["total"] == pytest.approx(80.0)
        assert "transportation" in categories

    def test_alerts_zero_budget_no_division_error(
        self, client: TestClient, db: Session
    ) -> None:
        """User with zero budget: percentage_used is 0.0 (no division by zero)."""
        user = User(
            username="zerobudgetuser",
            hashed_password=get_password_hash(
                "Password123!"
            ),  # pragma: allowlist secret
            budget=0.0,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.commit()

        token_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "zerobudgetuser",
                "password": "Password123!",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        token = token_response.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})

        response = client.get("/api/v1/alerts/")
        assert response.status_code == 200
        assert response.json()["percentage_used"] == 0.0

    def test_alerts_response_shape(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Response contains all expected fields."""
        response = authenticated_client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        for key in (
            "user_id",
            "username",
            "month",
            "total_spent",
            "budget",
            "status",
            "remaining",
            "percentage_used",
            "expenses_by_category",
        ):
            assert key in data
        assert data["username"] == test_user.username

    def test_alerts_unauthorized(self, client: TestClient) -> None:
        """Without auth token returns 401."""
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 401
