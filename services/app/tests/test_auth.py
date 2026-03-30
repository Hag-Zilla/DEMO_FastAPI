"""Authentication and login endpoint tests."""

from fastapi.testclient import TestClient

from app.database.models.user import User


class TestLogin:
    """Test cases for /token endpoint."""

    def test_login_success(self, client: TestClient, test_user: User) -> None:
        """Test successful login returns JWT token."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword123",  # pragma: allowlist secret
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client: TestClient, test_user: User) -> None:
        """Test login with invalid password returns 401."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "wrongpassword",  # pragma: allowlist secret
            },
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with nonexistent username returns 401."""
        response = client.post(
            "/token",
            data={
                "username": "nonexistent",
                "password": "anypassword",  # pragma: allowlist secret
            },
        )
        assert response.status_code == 401

    def test_login_pending_user_fails(
        self, client: TestClient, test_pending_user: User
    ) -> None:
        """Test that PENDING users cannot login."""
        response = client.post(
            "/token",
            data={
                "username": "pendinguser",
                "password": "pendingpass123",  # pragma: allowlist secret
            },
        )
        assert response.status_code == 403
        assert "User account is not active" in response.json()["detail"]

    def test_token_format(self, client: TestClient, test_user: User) -> None:
        """Test that returned token is in proper JWT format."""
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword123",  # pragma: allowlist secret
            },
        )
        token = response.json()["access_token"]
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3, "Invalid JWT token format"


class TestCurrentUser:
    """Test cases for /users/me endpoint."""

    def test_get_current_user_success(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Test retrieving current user profile."""
        response = authenticated_client.get("/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["id"] == test_user.id

    def test_get_current_user_unauthorized(self, client: TestClient) -> None:
        """Test accessing /users/me without token returns 403."""
        response = client.get("/users/me")
        assert response.status_code == 403

    def test_get_current_user_invalid_token(self, client: TestClient) -> None:
        """Test accessing /users/me with invalid token returns 403."""
        client.headers.update({"Authorization": "Bearer invalidtoken"})
        response = client.get("/users/me")
        assert response.status_code == 403
