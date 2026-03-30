"""Expense report endpoint tests."""

import pytest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import ExpenseCategory, UserRole, UserStatus
from app.core.security import get_password_hash
from app.database.models.expense import Expense
from app.database.models.user import User


class TestMonthlyReport:
    """Test cases for GET /reports/monthly/{year}/{month} endpoint."""

    def test_monthly_report_empty(self, authenticated_client: TestClient) -> None:
        """Monthly report with no expenses returns zero totals."""
        response = authenticated_client.get("/reports/monthly/2025/1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_expenses"] == 0.0
        assert data["count"] == 0
        assert data["average"] == 0.0
        assert data["period"] == "2025-01"
        assert data["period_type"] == "monthly"

    def test_monthly_report_with_expenses(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Monthly report sums expenses and computes average correctly."""
        db.add_all(
            [
                Expense(
                    description="Jan food",
                    amount=100.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime(2025, 1, 15, tzinfo=timezone.utc),
                ),
                Expense(
                    description="Jan transport",
                    amount=50.0,
                    category=ExpenseCategory.TRANSPORTATION,
                    user_id=test_user.id,
                    date=datetime(2025, 1, 20, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get("/reports/monthly/2025/1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_expenses"] == pytest.approx(150.0)
        assert data["count"] == 2
        assert data["average"] == pytest.approx(75.0)
        assert "food" in data["by_category"]
        assert "transportation" in data["by_category"]

    def test_monthly_report_december_boundary(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """December report excludes January expenses of the next year."""
        db.add_all(
            [
                Expense(
                    description="Dec",
                    amount=200.0,
                    category=ExpenseCategory.OTHER,
                    user_id=test_user.id,
                    date=datetime(2024, 12, 25, tzinfo=timezone.utc),
                ),
                Expense(
                    description="Jan",
                    amount=300.0,
                    category=ExpenseCategory.OTHER,
                    user_id=test_user.id,
                    date=datetime(2025, 1, 1, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get("/reports/monthly/2024/12")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["total_expenses"] == pytest.approx(200.0)

    def test_monthly_report_only_own_expenses(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """User only sees their own expenses in the report."""
        other_user = User(
            username="otherreportuser",
            hashed_password=get_password_hash(
                "Password123!"
            ),  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(other_user)
        db.commit()

        db.add_all(
            [
                Expense(
                    description="Others",
                    amount=9999.0,
                    category=ExpenseCategory.OTHER,
                    user_id=other_user.id,
                    date=datetime(2025, 1, 10, tzinfo=timezone.utc),
                ),
                Expense(
                    description="Mine",
                    amount=50.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime(2025, 1, 10, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get("/reports/monthly/2025/1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_expenses"] == pytest.approx(50.0)

    def test_monthly_report_unauthorized(self, client: TestClient) -> None:
        """Without auth token returns 401."""
        response = client.get("/reports/monthly/2025/1")
        assert response.status_code == 401


class TestPeriodReport:
    """Test cases for GET /reports/period endpoint."""

    def test_period_report_basic(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Expenses inside the range are included; outside are excluded."""
        db.add_all(
            [
                Expense(
                    description="In range",
                    amount=75.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime(2025, 3, 15, tzinfo=timezone.utc),
                ),
                Expense(
                    description="Out of range",
                    amount=500.0,
                    category=ExpenseCategory.OTHER,
                    user_id=test_user.id,
                    date=datetime(2025, 6, 1, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get(
            "/reports/period",
            params={
                "start_date": "2025-03-01T00:00:00",
                "end_date": "2025-03-31T23:59:59",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["total_expenses"] == pytest.approx(75.0)
        assert data["period_type"] == "custom"

    def test_period_report_empty(self, authenticated_client: TestClient) -> None:
        """Period with no expenses returns zero totals."""
        response = authenticated_client.get(
            "/reports/period",
            params={
                "start_date": "2020-01-01T00:00:00",
                "end_date": "2020-01-31T00:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_expenses"] == 0.0
        assert data["count"] == 0

    def test_period_report_average(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Average is computed correctly over multiple expenses."""
        db.add_all(
            [
                Expense(
                    description="e1",
                    amount=60.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime(2025, 2, 5, tzinfo=timezone.utc),
                ),
                Expense(
                    description="e2",
                    amount=90.0,
                    category=ExpenseCategory.FOOD,
                    user_id=test_user.id,
                    date=datetime(2025, 2, 10, tzinfo=timezone.utc),
                ),
            ]
        )
        db.commit()

        response = authenticated_client.get(
            "/reports/period",
            params={
                "start_date": "2025-02-01T00:00:00",
                "end_date": "2025-02-28T00:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["average"] == pytest.approx(75.0)  # (60+90)/2

    def test_period_report_unauthorized(self, client: TestClient) -> None:
        """Without auth token returns 401."""
        response = client.get(
            "/reports/period",
            params={
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T00:00:00",
            },
        )
        assert response.status_code == 401


class TestAdminAllReports:
    """Test cases for GET /reports/all endpoint (admin only)."""

    def test_admin_all_reports_structure(
        self, admin_client: TestClient, test_expense: Expense
    ) -> None:
        """Admin receives a well-formed all-users report."""
        response = admin_client.get("/reports/all")
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "admin_all_users"
        assert "total_across_users" in data
        assert "total_expenses_count" in data
        assert "by_user" in data
        assert len(data["by_user"]) >= 1

    def test_admin_all_reports_totals(
        self, admin_client: TestClient, test_expense: Expense
    ) -> None:
        """Total across users reflects the fixture expense amount."""
        response = admin_client.get("/reports/all")
        assert response.status_code == 200
        data = response.json()
        assert data["total_expenses_count"] >= 1
        assert data["total_across_users"] >= 25.50  # test_expense.amount

    def test_non_admin_cannot_access_all_reports(
        self, authenticated_client: TestClient
    ) -> None:
        """Regular user is forbidden from GET /reports/all (403)."""
        response = authenticated_client.get("/reports/all")
        assert response.status_code == 403

    def test_admin_all_reports_unauthorized(self, client: TestClient) -> None:
        """Without auth token returns 401."""
        response = client.get("/reports/all")
        assert response.status_code == 401
