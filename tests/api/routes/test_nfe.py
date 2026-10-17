"""Tests for NFC-e import API routes.

This module validates the HTTP behavior of the NFC-e import endpoint.

The tests isolate the route from external services, scraping, enrichment,
and database persistence by replacing the authenticated user and NFE
pipeline dependencies.

The route tests verify that:

- authentication is required;
- the authenticated user's identifier is forwarded to the pipeline;
- the QR Code URL is forwarded correctly;
- a successfully imported NFC-e returns HTTP 201;
- the persisted NFE is serialized according to NFEImportResponse.

Pipeline behavior itself is tested separately in the service layer.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from httpx import AsyncClient

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.nfe import get_nfe_pipeline
from app.main import app
from app.models.nfe import NFE
from app.models.user import User
from app.services.nfe_pipeline import NfePipeline


@pytest.mark.asyncio
async def test_import_nfe_returns_created_nfe(
    client: AsyncClient,
) -> None:
    """Return HTTP 201 and the imported NFC-e when processing succeeds."""

    user = Mock(spec=User)
    user.id = 10

    nfe = Mock(spec=NFE)
    nfe.id = 20
    nfe.nfe_key = "12345678901234567890123456789012345678901234"
    nfe.nfe_date = datetime(2026, 10, 16, 12, 30)
    nfe.market_id = 30
    nfe.user_id = user.id

    pipeline = Mock(spec=NfePipeline)
    pipeline.process = AsyncMock(return_value=nfe)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_nfe_pipeline] = lambda: pipeline

    try:
        response = await client.post(
            "/api/v1/nfes/import",
            json={
                "qr_code_url": (
                    "https://example.com/nfce?"
                    "p=12345678901234567890123456789012345678901234"
                )
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201

    body = response.json()

    assert body["id"] == nfe.id
    assert body["nfe_key"] == nfe.nfe_key
    assert body["market_id"] == nfe.market_id
    assert body["user_id"] == user.id

    pipeline.process.assert_awaited_once_with(
        qr_code_url=(
            "https://example.com/nfce?"
            "p=12345678901234567890123456789012345678901234"
        ),
        user_id=user.id,
    )


@pytest.mark.asyncio
async def test_import_nfe_requires_authentication(
    client: AsyncClient,
) -> None:
    """Reject NFC-e import requests without authentication."""

    response = await client.post(
        "/api/v1/nfes/import",
        json={
            "qr_code_url": "https://example.com/nfce"
        },
    )

    assert response.status_code == 401