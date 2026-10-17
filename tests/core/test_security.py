"""Tests for password verification and JWT security utilities."""

from datetime import timedelta

import jwt
import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.core.config import get_settings


settings = get_settings()


def test_verify_password_with_valid_password() -> None:
    """Return True when the plain password matches the stored hash."""

    from passlib.context import CryptContext

    context = CryptContext(
        schemes=["bcrypt_sha256"],
        deprecated="auto",
    )

    password = "StrongPassword123"
    hashed_password = context.hash(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_with_invalid_password() -> None:
    """Return False when the plain password does not match the hash."""

    from passlib.context import CryptContext

    context = CryptContext(
        schemes=["bcrypt_sha256"],
        deprecated="auto",
    )

    hashed_password = context.hash("CorrectPassword123")

    assert verify_password(
        "WrongPassword123",
        hashed_password,
    ) is False


def test_create_and_decode_access_token() -> None:
    """Create a token containing the expected subject."""

    token = create_access_token(subject="123")

    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert "exp" in payload


def test_decode_expired_access_token() -> None:
    """Reject an expired JWT access token."""

    token = create_access_token(
        subject="123",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_decode_invalid_access_token() -> None:
    """Reject a JWT signed with an invalid secret."""

    token = jwt.encode(
        {"sub": "123"},
        "invalid-test-secret-with-at-least-32-bytes",
        algorithm=settings.algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)