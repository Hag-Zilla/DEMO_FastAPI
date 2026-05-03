"""Expense management endpoint tests."""
# pylint: disable=unused-argument  # pytest fixtures are injected for side effects

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from services.api.core.enums import ExpenseCategory, UserRole, UserStatus
from services.api.core.security import get_password_hash
from services.api.database.models.expense import Expense
from services.api.database.models.user import User


class TestCreateExpense:
    """Test cases for POST /expenses/ endpoint."""

    def test_create_expense_success(
        self, authenticated_client: TestClient, test_user
    ) -> None:
        """Test successful expense creation."""
        response = authenticated_client.post(
            "/api/v1/expenses/",
            json={
                "description": "Lunch",
                "amount": 25.50,
                "category": "food",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Lunch"
        assert data["amount"] == 25.50
        assert data["category"] == "food"
        assert data["user_id"] == test_user.id

    def test_create_expense_unauthorized(self, client: TestClient) -> None:
        """Test creating expense without authentication."""
        response = client.post(
            "/api/v1/expenses/",
            json={
                "description": "Lunch",
                "amount": 25.50,
                "category": "food",
            },
        )
        assert response.status_code == 401

    def test_create_expense_invalid_category(
        self, authenticated_client: TestClient
    ) -> None:
        """Test creating expense with invalid category."""
        response = authenticated_client.post(
            "/api/v1/expenses/",
            json={
                "description": "Test",
                "amount": 10.0,
                "category": "invalid_category",
            },
        )
        assert response.status_code == 422  # Validation error


class TestListExpenses:
    """Test cases for GET /expenses/ endpoint."""

    def test_list_expenses_empty(self, authenticated_client: TestClient) -> None:
        """Test listing expenses when none exist."""
        response = authenticated_client.get("/api/v1/expenses/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["data"] == []

    def test_list_expenses_by_user(
        self, authenticated_client: TestClient, test_expense: Expense
    ) -> None:
        """Test that users only see their own expenses."""
        response = authenticated_client.get("/api/v1/expenses/")
        assert response.status_code == 200
        payload = response.json()
        expenses = payload["data"]
        assert payload["count"] == 1
        assert len(expenses) == 1
        assert expenses[0]["id"] == test_expense.id

    def test_list_expenses_filter_by_category(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test filtering expenses by category."""
        response = authenticated_client.get("/api/v1/expenses/?category=food")
        assert response.status_code == 200
        expenses = response.json()["data"]
        assert len(expenses) > 0
        assert all(e["category"] == "food" for e in expenses)

    def test_list_expenses_filter_by_date_range(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test filtering expenses by date range."""
        start_date = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        end_date = datetime.now(timezone.utc).isoformat()
        response = authenticated_client.get(
            "/api/v1/expenses/",
            params={"start_date": start_date, "end_date": end_date},
        )
        assert response.status_code == 200
        # Should have results within the date range
        assert response.json()["count"] > 0

    def test_list_expenses_pagination(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test that limit/offset pagination works correctly."""
        response_page1 = authenticated_client.get("/api/v1/expenses/?limit=2&offset=0")
        response_page2 = authenticated_client.get("/api/v1/expenses/?limit=2&offset=2")
        assert response_page1.status_code == 200
        assert response_page2.status_code == 200
        page1_ids = [e["id"] for e in response_page1.json()["data"]]
        page2_ids = [e["id"] for e in response_page2.json()["data"]]
        # Pages must not overlap
        assert len(page1_ids) == 2
        assert len(set(page1_ids) & set(page2_ids)) == 0

    def test_list_expenses_includes_total(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test that list_expenses returns total count separate from page size."""
        response = authenticated_client.get("/api/v1/expenses/?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "count" in data
        assert data["total"] >= data["count"]  # total is unaffected by limit
        assert data["total"] == len(multiple_expenses)
        assert data["count"] == 1  # page size

    def test_list_expenses_admin_sees_all(
        self, admin_client: TestClient, test_expense: Expense, db: Session
    ) -> None:
        """Test that admins can see all users' expenses."""
        another_user = User(
            username="otheruser",
            hashed_password=get_password_hash("password"),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(another_user)
        db.commit()
        db.refresh(another_user)

        other_expense = Expense(
            description="Other user expense",
            amount=100.0,
            category=ExpenseCategory.ENTERTAINMENT,
            user_id=another_user.id,
        )
        db.add(other_expense)
        db.commit()

        # Admin should see multiple expenses
        response = admin_client.get("/api/v1/expenses/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["count"] >= 2
        assert len(payload["data"]) >= 2


class TestUpdateDeleteExpense:
    """Test cases for PUT/DELETE /expenses/{id} endpoints."""

    def test_update_expense_success(
        self, authenticated_client: TestClient, test_expense: Expense
    ) -> None:
        """Test updating an expense."""
        response = authenticated_client.put(
            f"/api/v1/expenses/{test_expense.id}",
            json={
                "description": "Updated meal",
                "amount": 35.00,
                "category": "food",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated meal"
        assert data["amount"] == 35.00

    def test_update_expense_not_found(self, authenticated_client: TestClient) -> None:
        """Test updating nonexistent expense."""
        response = authenticated_client.put(
            "/api/v1/expenses/99999",
            json={
                "description": "Update",
                "amount": 10.0,
                "category": "food",
            },
        )
        assert response.status_code == 404

    def test_delete_expense_success(
        self, authenticated_client: TestClient, test_expense: Expense
    ) -> None:
        """Test deleting an expense."""
        response = authenticated_client.delete(f"/api/v1/expenses/{test_expense.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = authenticated_client.get(f"/api/v1/expenses/{test_expense.id}")
        assert response.status_code == 404

    def test_user_cannot_access_others_expense(
        self, authenticated_client: TestClient, test_expense: Expense, db: Session
    ) -> None:
        """Test that users cannot GET another user's expense (returns 404 not 403)."""
        another_user = User(
            username="otheruser2",
            hashed_password=get_password_hash("password"),  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(another_user)
        db.commit()

        other_expense = Expense(
            description="Secret expense",
            amount=999.0,
            category=ExpenseCategory.OTHER,
            user_id=another_user.id,
        )
        db.add(other_expense)
        db.commit()

        # GET → 404, not 403: avoid revealing resource existence
        response = authenticated_client.get(f"/api/v1/expenses/{other_expense.id}")
        assert response.status_code == 404

    def test_user_cannot_update_others_expense(
        self, authenticated_client: TestClient, db: Session
    ) -> None:
        """Test that users cannot PUT to another user's expense."""
        another_user = User(
            username="otheruser3",
            hashed_password=get_password_hash("password"),  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(another_user)
        db.commit()

        other_expense = Expense(
            description="Private expense",
            amount=50.0,
            category=ExpenseCategory.OTHER,
            user_id=another_user.id,
        )
        db.add(other_expense)
        db.commit()

        response = authenticated_client.put(
            f"/api/v1/expenses/{other_expense.id}",
            json={"description": "Hacked", "amount": 1.0, "category": "food"},
        )
        assert response.status_code == 404

    def test_user_cannot_delete_others_expense(
        self, authenticated_client: TestClient, db: Session
    ) -> None:
        """Test that users cannot DELETE another user's expense."""
        another_user = User(
            username="otheruser4",
            hashed_password=get_password_hash("password"),  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(another_user)
        db.commit()

        other_expense = Expense(
            description="Do not delete",
            amount=75.0,
            category=ExpenseCategory.OTHER,
            user_id=another_user.id,
        )
        db.add(other_expense)
        db.commit()

        response = authenticated_client.delete(f"/api/v1/expenses/{other_expense.id}")
        assert response.status_code == 404
