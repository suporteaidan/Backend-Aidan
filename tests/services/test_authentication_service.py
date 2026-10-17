"""Tests for AuthenticationService."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.authentication_service import AuthenticationService


@pytest.mark.asyncio
async def test_authenticate_returns_user_with_valid_credentials() -> None:
    """Return the user when email and password are valid."""

    user = Mock(spec=User)
    user.password_hash = "stored-hash"

    repository = Mock(spec=UserRepository)
    repository.get_by_email = AsyncMock(
        return_value=user,
    )

    service = AuthenticationService(repository)

    with patch(
        "app.services.authentication_service.verify_password",
        return_value=True,
    ) as verify_password:
        result = await service.authenticate(
            email="user@example.com",
            password="ValidPassword123",
        )

    repository.get_by_email.assert_awaited_once_with(
        "user@example.com"
    )

    verify_password.assert_called_once_with(
        "ValidPassword123",
        "stored-hash",
    )

    assert result is user


@pytest.mark.asyncio
async def test_authenticate_returns_none_when_email_does_not_exist() -> None:
    """Return None when no user exists for the provided email."""

    repository = Mock(spec=UserRepository)
    repository.get_by_email = AsyncMock(
        return_value=None,
    )

    service = AuthenticationService(repository)

    result = await service.authenticate(
        email="missing@example.com",
        password="Password123",
    )

    repository.get_by_email.assert_awaited_once_with(
        "missing@example.com"
    )

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_returns_none_with_invalid_password() -> None:
    """Return None when the supplied password is invalid."""

    user = Mock(spec=User)
    user.password_hash = "stored-hash"

    repository = Mock(spec=UserRepository)
    repository.get_by_email = AsyncMock(
        return_value=user,
    )

    service = AuthenticationService(repository)

    with patch(
        "app.services.authentication_service.verify_password",
        return_value=False,
    ):
        result = await service.authenticate(
            email="user@example.com",
            password="WrongPassword",
        )

    assert result is None