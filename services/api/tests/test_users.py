"""User management endpoint tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from services.api.database.models.user import User
from services.api.core.enums import UserRole, UserStatus


class TestCreateUser:
    """Test cases for POST /users/create endpoint."""

    def test_create_user_success(self, client: TestClient, db: Session) -> None:
        """Test successful user creation."""
        response = client.post(
            "/api/v1/users/create",
            json={
                "username": "newuser",
                "password": "NewPassword123!",  # pragma: allowlist secret
                "budget": 1500.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["status"] == "pending"
        assert data["role"] == "user"
        assert data["budget"] == 1500.0

        # Verify in database
        user = db.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.status == UserStatus.PENDING

    def test_create_user_duplicate_username(
        self, client: TestClient, test_user: User
    ) -> None:
        """Test creating user with existing username returns 409."""
        response = client.post(
            "/api/v1/users/create",
            json={
                "username": "testuser",  # Already exists
                "password": "AnotherPassword123!",  # pragma: allowlist secret
                "budget": 1000.0,
            },
        )
        assert response.status_code == 409
        assert "already taken" in response.json()["detail"]

    def test_create_user_weak_password(self, client: TestClient) -> None:
        """Test creating user with weak password."""
        response = client.post(
            "/api/v1/users/create",
            json={
                "username": "weakpass",
                "password": "weak",  # pragma: allowlist secret
                "budget": 500.0,
            },
        )
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_new_user_pending_status(self, client: TestClient, db: Session) -> None:
        """Test that new users start in PENDING status."""
        response = client.post(
            "/api/v1/users/create",
            json={
                "username": "pendingcheck",
                "password": "SafePassword123!",  # pragma: allowlist secret
                "budget": 1000.0,
            },
        )
        assert response.status_code == 201
        user = db.query(User).filter(User.username == "pendingcheck").first()
        assert user is not None
        assert user.status == UserStatus.PENDING


class TestAdminUserOperations:
    """Test cases for admin user management endpoints."""

    def test_list_users_by_status(self, admin_client: TestClient, db: Session) -> None:
        """Test listing users filtered by status."""
        # Create users with different statuses (do NOT delete testadmin - it would invalidate the token)
        active_user = User(
            username="active1",
            hashed_password="hashed",  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=1000.0,
        )
        pending_user = User(
            username="pending1",
            hashed_password="hashed",  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.PENDING,
            budget=1000.0,
        )
        db.add(active_user)
        db.add(pending_user)
        db.commit()

        # List active users
        response = admin_client.get("/api/v1/users/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(user["status"] == "active" for user in data)

    def test_approve_user(
        self, admin_client: TestClient, test_pending_user: User, db: Session
    ) -> None:
        """Test admin approving a pending user."""
        response = admin_client.post(f"/api/v1/users/{test_pending_user.id}/approve")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

        # Verify in database (re-query since session was closed after the request)
        updated_user = db.get(User, test_pending_user.id)
        assert updated_user is not None
        assert updated_user.status == UserStatus.ACTIVE

    def test_approve_user_not_found(self, admin_client: TestClient) -> None:
        """Test approving nonexistent user returns 404."""
        response = admin_client.post("/api/v1/users/99999/approve")
        assert response.status_code == 404

    def test_admin_update_user(self, admin_client: TestClient, test_user: User) -> None:
        """Test admin updating user fields."""
        response = admin_client.put(
            f"/api/v1/users/update/{test_user.id}/",
            json={
                "username": "renameduser",
                "budget": 2000.0,
                "status": "active",
                "role": "user",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "renameduser"
        assert data["budget"] == 2000.0

    def test_delete_user(self, admin_client: TestClient, db: Session) -> None:
        """Test admin deleting a user."""
        # Create a user to delete
        user_to_delete = User(
            username="todelete",
            hashed_password="hashed",  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=500.0,
        )
        db.add(user_to_delete)
        db.commit()
        user_id = user_to_delete.id

        # Delete it
        response = admin_client.delete(f"/api/v1/users/delete/{user_id}/")
        assert response.status_code == 204

        # Verify it's deleted
        user = db.query(User).filter(User.id == user_id).first()
        assert user is None


class TestUserSelfOperations:
    """Test cases for user self-service operations."""

    def test_self_update_username(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Test user updating their own username."""
        response = authenticated_client.put(
            "/api/v1/users/update/",
            json={
                "username": "newusername",
                "budget": None,
                "password": None,
            },
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"

    def test_self_update_password(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Test user updating their own password."""
        response = authenticated_client.put(
            "/api/v1/users/update/",
            json={
                "username": None,
                "budget": None,
                "password": "NewPassword123!",  # pragma: allowlist secret
            },
        )
        assert response.status_code == 200
        # Old password should no longer work
        login_response = authenticated_client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "testpassword123",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert login_response.status_code == 401

    def test_self_update_duplicate_username(
        self, authenticated_client: TestClient, test_user: User, db: Session
    ) -> None:
        """Test that updating to an already-taken username returns 409."""
        # Create a second user whose username we will try to steal
        existing = User(
            username="takenusername",
            hashed_password="hashed",  # pragma: allowlist secret
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            budget=500.0,
        )
        db.add(existing)
        db.commit()

        response = authenticated_client.put(
            "/api/v1/users/update/",
            json={"username": "takenusername", "budget": None, "password": None},
        )
        assert response.status_code == 409
        assert "already taken" in response.json()["detail"]


class TestRBACAdminRoutes:
    """Verify that regular users cannot access admin-only endpoints."""

    def test_non_admin_cannot_list_users(
        self, authenticated_client: TestClient
    ) -> None:
        """Regular user is forbidden from GET /users/."""
        response = authenticated_client.get("/api/v1/users/")
        assert response.status_code == 403

    def test_non_admin_cannot_approve_user(
        self, authenticated_client: TestClient, test_pending_user: User
    ) -> None:
        """Regular user is forbidden from POST /users/{id}/approve."""
        response = authenticated_client.post(
            f"/api/v1/users/{test_pending_user.id}/approve"
        )
        assert response.status_code == 403

    def test_non_admin_cannot_admin_update_user(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Regular user is forbidden from PUT /users/update/{id}/."""
        response = authenticated_client.put(
            f"/api/v1/users/update/{test_user.id}/",
            json={
                "username": "hack",
                "budget": 0.0,
                "status": "active",
                "role": "admin",
            },
        )
        assert response.status_code == 403

    def test_non_admin_cannot_delete_user(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Regular user is forbidden from DELETE /users/delete/{id}/."""
        response = authenticated_client.delete(f"/api/v1/users/delete/{test_user.id}/")
        assert response.status_code == 403
