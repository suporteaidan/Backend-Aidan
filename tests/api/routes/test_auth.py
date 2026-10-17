"""Tests for authentication API routes."""

from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient

from app.api.v1.routes.auth import get_authentication_service
from app.main import app
from app.models.user import User
from app.services.authentication_service import AuthenticationService


@pytest.mark.asyncio
async def test_login_returns_access_token(
    client: AsyncClient,
) -> None:
    """Return a JWT access token when credentials are valid."""

    user = Mock(spec=User)
    user.id = 10

    authentication_service = Mock(
        spec=AuthenticationService,
    )
    authentication_service.authenticate = AsyncMock(
        return_value=user,
    )

    app.dependency_overrides[
        get_authentication_service
    ] = lambda: authentication_service

    try:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "user@example.com",
                "password": "ValidPassword123",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["token_type"] == "bearer"

    authentication_service.authenticate.assert_awaited_once_with(
        email="user@example.com",
        password="ValidPassword123",
    )


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(
    client: AsyncClient,
) -> None:
    """Return HTTP 401 when credentials are invalid."""

    authentication_service = Mock(
        spec=AuthenticationService,
    )
    authentication_service.authenticate = AsyncMock(
        return_value=None,
    )

    app.dependency_overrides[
        get_authentication_service
    ] = lambda: authentication_service

    try:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "user@example.com",
                "password": "WrongPassword",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect email or password."
    }