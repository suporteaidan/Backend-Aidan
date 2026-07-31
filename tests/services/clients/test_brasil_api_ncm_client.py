"""Tests for the BrasilAPI NCM client with Mock."""

import pytest
import httpx

from app.services.clients.brasil_api_ncm_client import BrasilApiNcmClient
from app.exceptions.external_provider import ExternalProviderError, ExternalProviderResponseError

@pytest.mark.asyncio
async def test_search_by_description_returns_suggestion() -> None:
    """Return normalized NCM suggestions from a valid provider response."""

    async def handler(request: httpx.Request) -> httpx.Response:

        assert request.url.params["search"] == "CAFE TORRADO 500G"

        return httpx.Response(
            status_code = 200,
            json = [
                {
                    "codigo": "09.01.21.00",
                    "descricao": "Cafe torrado, nao descafeinado",
                },
                {
                    "codigo": "09.01.22.00",
                    "descricao": "Cafe torrado, descafeinado",
                },
            ]
        )
    
    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:

        ncm_client = BrasilApiNcmClient(client)

        suggestions = await ncm_client.search_by_description(
            "CAFE TORRADO 500G"
        )

    assert len(suggestions) == 2
    assert suggestions[0].code == "09.01.21.00"
    assert suggestions[0].description == "Cafe torrado, nao descafeinado"
    assert suggestions[1].code == "09.01.22.00"

@pytest.mark.asyncio
async def test_search_by_description_returns_empty_list() -> None:
    """Return an empty list when the provider finds no NCM suggestions."""

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=[],
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        ncm_client = BrasilApiNcmClient(client)

        suggestions = await ncm_client.search_by_description(
            "UNKNOWN PRODUCT"
        )

    assert suggestions == []

@pytest.mark.asyncio
async def test_search_by_description_raises_provider_error_on_http_error() -> None:
    """Raise ExternalProviderError when BrasilAPI returns an HTTP error."""

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        ncm_client = BrasilApiNcmClient(client)

        with pytest.raises(ExternalProviderError):
            await ncm_client.search_by_description("CAFE")

@pytest.mark.asyncio
async def test_search_by_description_raises_response_error_for_invalid_format() -> None:
    """Raise an error when the provider response is not a list."""

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"results": []},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        ncm_client = BrasilApiNcmClient(client)

        with pytest.raises(ExternalProviderResponseError):
            await ncm_client.search_by_description("CAFE")

@pytest.mark.asyncio
async def test_search_by_description_raises_response_error_for_invalid_item() -> None:
    """Raise an error when an NCM item has an invalid structure."""

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=[
                {
                    "codigo": None,
                    "descricao": "Invalid NCM",
                }
            ],
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        ncm_client = BrasilApiNcmClient(client)

        with pytest.raises(ExternalProviderResponseError):
            await ncm_client.search_by_description("CAFE")