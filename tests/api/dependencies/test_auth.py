"""Tests for authentication dependencies."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_get_current_user_returns_authenticated_user() -> None:
    """Return the user identified by a valid JWT subject."""

    user = Mock(spec=User)
    user.id = 10

    repository = Mock(spec=UserRepository)
    repository.get_by_id = AsyncMock(
        return_value=user,
    )

    with patch(
        "app.api.dependencies.auth.decode_access_token",
        return_value={"sub": "10"},
    ):
        result = await get_current_user(
            token="valid-token",
            user_repository=repository,
        )

    repository.get_by_id.assert_awaited_once_with(10)

    assert result is user


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token() -> None:
    """Raise HTTP 401 when JWT validation fails."""

    repository = Mock(spec=UserRepository)

    with patch(
        "app.api.dependencies.auth.decode_access_token",
        side_effect=InvalidTokenError(),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="invalid-token",
                user_repository=repository,
            )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_subject() -> None:
    """Raise HTTP 401 when the JWT does not contain a subject."""

    repository = Mock(spec=UserRepository)

    with patch(
        "app.api.dependencies.auth.decode_access_token",
        return_value={},
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="token",
                user_repository=repository,
            )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_non_numeric_subject() -> None:
    """Raise HTTP 401 when the JWT subject is not a user identifier."""

    repository = Mock(spec=UserRepository)

    with patch(
        "app.api.dependencies.auth.decode_access_token",
        return_value={"sub": "invalid-user-id"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="token",
                user_repository=repository,
            )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user() -> None:
    """Raise HTTP 401 when the JWT user no longer exists."""

    repository = Mock(spec=UserRepository)
    repository.get_by_id = AsyncMock(
        return_value=None,
    )

    with patch(
        "app.api.dependencies.auth.decode_access_token",
        return_value={"sub": "10"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                token="token",
                user_repository=repository,
            )

    repository.get_by_id.assert_awaited_once_with(10)

    assert exc_info.value.status_code == 401