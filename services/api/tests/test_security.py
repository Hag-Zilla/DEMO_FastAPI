"""Security utility unit tests — password hashing and JWT (no HTTP layer)."""

import pytest
from datetime import timedelta

from services.api.core.exceptions import AuthenticationException
from services.api.core.security import (
    create_access_token,
    decode_jwt_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for get_password_hash / verify_password."""

    def test_hash_and_verify_roundtrip(self) -> None:
        """Hashing then verifying the same password succeeds."""
        password = "TestPassword123!"  # pragma: allowlist secret
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails_verification(self) -> None:
        """A wrong password does not verify against the hash."""
        hashed = get_password_hash("correct_password")  # pragma: allowlist secret
        assert not verify_password("wrong_password", hashed)  # pragma: allowlist secret

    def test_hash_is_not_plaintext(self) -> None:
        """The hash value differs from the original password."""
        password = "SomePassword!"  # pragma: allowlist secret
        assert get_password_hash(password) != password

    def test_argon2_produces_unique_hashes(self) -> None:
        """Argon2 uses a random salt: same input yields different hashes."""
        h1 = get_password_hash("same_password")  # pragma: allowlist secret
        h2 = get_password_hash("same_password")  # pragma: allowlist secret
        assert h1 != h2
        assert verify_password("same_password", h1)  # pragma: allowlist secret
        assert verify_password("same_password", h2)  # pragma: allowlist secret


class TestJWT:
    """Tests for create_access_token / decode_jwt_token."""

    def test_decode_valid_token(self) -> None:
        """A freshly minted token decodes and contains the expected subject."""
        token = create_access_token({"sub": "testuser"}, timedelta(minutes=30))
        payload = decode_jwt_token(token)
        assert payload["sub"] == "testuser"

    def test_decode_expired_token_raises(self) -> None:
        """An already-expired token raises AuthenticationException."""
        token = create_access_token({"sub": "testuser"}, timedelta(seconds=-1))
        with pytest.raises(AuthenticationException):
            decode_jwt_token(token)

    def test_decode_garbage_token_raises(self) -> None:
        """A completely invalid string raises AuthenticationException."""
        with pytest.raises(AuthenticationException):
            decode_jwt_token("not.a.valid.token")

    def test_decode_tampered_signature_raises(self) -> None:
        """Tampering with the signature portion raises AuthenticationException."""
        token = create_access_token({"sub": "testuser"}, timedelta(minutes=30))
        tampered = token[:-10] + "XXXXXXXXXX"
        with pytest.raises(AuthenticationException):
            decode_jwt_token(tampered)

    def test_token_contains_expiry(self) -> None:
        """The decoded payload includes an 'exp' claim."""
        token = create_access_token({"sub": "alice"}, timedelta(minutes=15))
        payload = decode_jwt_token(token)
        assert "exp" in payload
