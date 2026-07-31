"""Tests for the NFC-e enrichment service."""

from decimal import Decimal
from datetime import datetime
import pytest

from app.services.clients.base_ncm_client import BaseNCMClient
from app.schemas.nfe_data import NCMSuggestionData, NFEMarketData, NFEData, NFEProductData
from app.services.enrichment.nfe_enrichment_service import NFEEnrichmentService
from app.exceptions.external_provider import ExternalProviderError

class FakeNCMClient(BaseNCMClient):
    """Fake NCM client used to provide deterministic test responses."""

    def __init__(self, suggestions: list[NCMSuggestionData] | None = None, error: Exception | None = None) -> None:
        """Initialize the fake client with a predefined result or error."""

        self._suggestions = suggestions or []
        self._error = error
        self._calls: list[str] = []

    async def search_by_description(self, description: str) -> list[NCMSuggestionData]:
        """Return predefined suggestions or raise the configured error."""

        self._calls.append(description)

        if self._error is not None:
            raise self._error

        return self._suggestions


@pytest.fixture
def market_data() -> NFEMarketData:
    """Return normalized market data for enrichment tests."""
    return NFEMarketData(
        cnpj="12345678000190",
        market_name="Market Test",
        market_street="Test Street",
        market_number="100",
        market_district="Downtown",
        market_city="Florianopolis",
        market_state="SC",
    )


def build_product(
    *,
    product_code: str,
    code_type: str,
    name: str,
    ncm_code: str | None = None,
) -> NFEProductData:
    """Build a product representation for enrichment tests."""
    return NFEProductData(
        product_code=product_code,
        code_type=code_type,
        name=name,
        unit_price=Decimal("10.00"),
        total_price=Decimal("20.00"),
        quantity=Decimal("2"),
        ncm_code=ncm_code,
        brand=None,
        picture_url=None,
    )


def build_nfe(
    market_data: NFEMarketData,
    products: list[NFEProductData],
) -> NFEData:
    """Build an NFC-e representation with the provided products."""
    return NFEData(
        nfe_key="12345678901234567890123456789012345678901234",
        nfe_date=datetime(2026, 7, 23, 10, 0, 0),
        market_data=market_data,
        products_data=products,
    )

@pytest.mark.asyncio
async def test_enrich_keeps_ean_product_unchanged(
    market_data: NFEMarketData,
) -> None:
    """Keep EAN products unchanged and skip NCM lookup."""
    client = FakeNCMClient(
        suggestions=[
            NCMSuggestionData(
                code="09.01.21.00",
                description="Coffee",
            )
        ]
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="7891234567890",
        code_type="EAN",
        name="COFFEE 500G",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert result.products_data[0] == product
    assert client._calls == []

@pytest.mark.asyncio
async def test_enrich_internal_product_with_first_ncm_suggestion(
    market_data: NFEMarketData,
) -> None:
    """Use the first NCM suggestion for an internal product."""
    client = FakeNCMClient(
        suggestions=[
            NCMSuggestionData(
                code="09.01.21.00",
                description="Coffee roasted",
            ),
            NCMSuggestionData(
                code="09.01.22.00",
                description="Coffee decaffeinated",
            ),
        ]
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="COFFEE ROASTED 500G",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    enriched_product = result.products_data[0]

    assert enriched_product.ncm_code == "09012100"
    assert enriched_product.product_code == product.product_code
    assert enriched_product.unit_price == product.unit_price
    assert enriched_product.total_price == product.total_price
    assert enriched_product.quantity == product.quantity
    assert client._calls == ["COFFEE ROASTED 500G"]

@pytest.mark.asyncio
async def test_enrich_skips_internal_product_with_existing_ncm(
    market_data: NFEMarketData,
) -> None:
    """Skip external lookup when an internal product already has an NCM."""
    client = FakeNCMClient(
        suggestions=[
            NCMSuggestionData(
                code="09.01.22.00",
                description="Other classification",
            )
        ]
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="COFFEE",
        ncm_code="09012100",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert result.products_data[0].ncm_code == "09012100"
    assert client._calls == []

@pytest.mark.asyncio
async def test_enrich_keeps_product_when_no_suggestion_is_found(
    market_data: NFEMarketData,
) -> None:
    """Keep the product unchanged when no NCM suggestion is available."""
    client = FakeNCMClient()
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="UNKNOWN PRODUCT",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert result.products_data[0] == product
    assert client._calls == ["UNKNOWN PRODUCT"]

@pytest.mark.asyncio
async def test_enrich_keeps_product_when_provider_fails(
    market_data: NFEMarketData,
) -> None:
    """Keep the product unchanged when the external NCM provider fails."""
    client = FakeNCMClient(
        error=ExternalProviderError("Provider unavailable"),
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="COFFEE",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert result.products_data[0] == product
    assert client._calls == ["COFFEE"]

@pytest.mark.asyncio
async def test_enrich_ignores_invalid_ncm_code(
    market_data: NFEMarketData,
) -> None:
    """Keep the product unchanged when the provider returns an invalid NCM."""
    client = FakeNCMClient(
        suggestions=[
            NCMSuggestionData(
                code="123",
                description="Invalid classification",
            )
        ]
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="TEST PRODUCT",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert result.products_data[0].ncm_code is None

@pytest.mark.asyncio
async def test_enrich_does_not_modify_original_nfe(
    market_data: NFEMarketData,
) -> None:
    """Return enriched data without mutating the original NFC-e object."""
    client = FakeNCMClient(
        suggestions=[
            NCMSuggestionData(
                code="09.01.21.00",
                description="Coffee",
            )
        ]
    )
    service = NFEEnrichmentService(client)

    product = build_product(
        product_code="ABC-001",
        code_type="INTERNAL",
        name="COFFEE",
    )
    nfe_data = build_nfe(market_data, [product])

    result = await service.enrich(nfe_data)

    assert nfe_data.products_data[0].ncm_code is None
    assert result.products_data[0].ncm_code == "09012100"
    assert result is not nfe_data