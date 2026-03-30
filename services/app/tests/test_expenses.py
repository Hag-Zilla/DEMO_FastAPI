"""Expense management endpoint tests."""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models.expense import Expense
from app.core.enums import ExpenseCategory


class TestCreateExpense:
    """Test cases for POST /expenses/ endpoint."""

    def test_create_expense_success(
        self, authenticated_client: TestClient, test_user
    ) -> None:
        """Test successful expense creation."""
        response = authenticated_client.post(
            "/expenses/",
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
            "/expenses/",
            json={
                "description": "Lunch",
                "amount": 25.50,
                "category": "food",
            },
        )
        assert response.status_code == 403

    def test_create_expense_invalid_category(
        self, authenticated_client: TestClient
    ) -> None:
        """Test creating expense with invalid category."""
        response = authenticated_client.post(
            "/expenses/",
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
        response = authenticated_client.get("/expenses/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_expenses_by_user(
        self, authenticated_client: TestClient, test_expense: Expense
    ) -> None:
        """Test that users only see their own expenses."""
        response = authenticated_client.get("/expenses/")
        assert response.status_code == 200
        expenses = response.json()
        assert len(expenses) == 1
        assert expenses[0]["id"] == test_expense.id

    def test_list_expenses_filter_by_category(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test filtering expenses by category."""
        response = authenticated_client.get("/expenses/?category=food")
        assert response.status_code == 200
        expenses = response.json()
        assert len(expenses) > 0
        assert all(e["category"] == "food" for e in expenses)

    def test_list_expenses_filter_by_date_range(
        self, authenticated_client: TestClient, multiple_expenses: list[Expense]
    ) -> None:
        """Test filtering expenses by date range."""
        start_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        end_date = datetime.utcnow().isoformat()
        response = authenticated_client.get(
            f"/expenses/?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
        # Should have results within the date range
        assert len(response.json()) > 0

    def test_list_expenses_admin_sees_all(
        self, admin_client: TestClient, test_expense: Expense, db: Session
    ) -> None:
        """Test that admins can see all users' expenses."""
        # Create another user's expense
        from app.database.models.user import User
        from app.database.models.expense import Expense
        from app.core.enums import UserRole, UserStatus
        from app.core.security import get_password_hash

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
        response = admin_client.get("/expenses/")
        assert response.status_code == 200
        expenses = response.json()
        assert len(expenses) >= 2


class TestUpdateDeleteExpense:
    """Test cases for PUT/DELETE /expenses/{id} endpoints."""

    def test_update_expense_success(
        self, authenticated_client: TestClient, test_expense: Expense
    ) -> None:
        """Test updating an expense."""
        response = authenticated_client.put(
            f"/expenses/{test_expense.id}",
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
            "/expenses/99999",
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
        response = authenticated_client.delete(f"/expenses/{test_expense.id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = authenticated_client.get(f"/expenses/{test_expense.id}")
        assert response.status_code == 404

    def test_user_cannot_access_others_expense(
        self, authenticated_client: TestClient, test_expense: Expense, db: Session
    ) -> None:
        """Test that users cannot access/modify other users' expenses."""
        from app.database.models.user import User
        from app.core.enums import UserRole, UserStatus
        from app.core.security import get_password_hash

        # Create another user
        another_user = User(
            username="otheruser2",
            hashed_password=get_password_hash("password"),
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        db.add(another_user)
        db.commit()

        # Try to update test_expense (owned by test_user via authenticated_client)
        # This is actually the current user's expense, so should work
        # Instead, create expense for another user
        from app.database.models.expense import Expense

        other_expense = Expense(
            description="Secret expense",
            amount=999.0,
            category=ExpenseCategory.OTHER,
            user_id=another_user.id,
        )
        db.add(other_expense)
        db.commit()

        # Current user (test_user) tries to access another user's expense
        response = authenticated_client.get(f"/expenses/{other_expense.id}")
        assert response.status_code == 403  # Forbidden
