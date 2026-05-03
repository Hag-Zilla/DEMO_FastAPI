"""Authentication and login endpoint tests."""
# pylint: disable=unused-argument  # pytest fixtures are injected for side effects

from fastapi.testclient import TestClient

from services.api.database.models.user import User


class TestLogin:
    """Test cases for /token endpoint."""

    def test_login_success(self, client: TestClient, test_user: User) -> None:
        """Test successful login returns JWT token."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "testpassword123",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client: TestClient, test_user: User) -> None:
        """Test login with invalid password returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "wrongpassword",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with nonexistent username returns 401."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent",
                "password": "anypassword",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert response.status_code == 401

    def test_login_pending_user_fails(
        self, client: TestClient, test_pending_user: User
    ) -> None:
        """Test that PENDING users cannot login."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "pendinguser",
                "password": "pendingpass123",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert response.status_code == 403
        assert "User account is not active" in response.json()["detail"]

    def test_login_disabled_user_fails(
        self, client: TestClient, test_disabled_user: User
    ) -> None:
        """Test that DISABLED users cannot login."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "disableduser",
                "password": "disabledpass123",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert response.status_code == 403
        assert "User account is not active" in response.json()["detail"]

    def test_token_format(self, client: TestClient, test_user: User) -> None:
        """Test that returned token is in proper JWT format."""
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "testpassword123",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        token = response.json()["access_token"]
        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3, "Invalid JWT token format"


class TestPasswordReset:
    """Test cases for password recovery and reset endpoints."""

    def test_password_recovery_generic_message(
        self, client: TestClient, test_user: User
    ) -> None:
        """Recovery endpoint returns generic message to avoid user enumeration."""
        response = client.post(
            "/api/v1/auth/password-recovery",
            json={"username": "testuser"},
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_password_reset_with_recovery_token(
        self, client: TestClient, test_user: User
    ) -> None:
        """A user can reset password using a recovery token."""
        recovery = client.post(
            "/api/v1/auth/password-recovery",
            json={"username": "testuser"},
        )
        assert recovery.status_code == 200
        token = recovery.json().get("reset_token")
        assert token is not None

        reset = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "BrandNewPassword123!",  # pragma: allowlist secret
            },
        )
        assert reset.status_code == 204

        login = client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "BrandNewPassword123!",  # pragma: allowlist secret
                "grant_type": "password",
            },
        )
        assert login.status_code == 200

    def test_password_reset_invalid_token(self, client: TestClient) -> None:
        """Invalid reset token is rejected."""
        reset = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid.token.value",
                "new_password": "BrandNewPassword123!",  # pragma: allowlist secret
            },
        )
        assert reset.status_code == 400


class TestCurrentUser:
    """Test cases for /users/me endpoint."""

    def test_get_current_user_success(
        self, authenticated_client: TestClient, test_user: User
    ) -> None:
        """Test retrieving current user profile."""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["id"] == test_user.id

    def test_get_current_user_unauthorized(self, client: TestClient) -> None:
        """Test accessing /users/me without token returns 401."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient) -> None:
        """Test accessing /users/me with invalid token returns 401."""
        client.headers.update({"Authorization": "Bearer invalidtoken"})
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
