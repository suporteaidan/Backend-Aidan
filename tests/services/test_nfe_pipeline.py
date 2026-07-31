"""Tests for the NFC-e processing pipeline."""


from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
import pytest

from app.schemas.nfe_data import NFEData,NFEMarketData,NFEProductData
from app.services.clients.nfe_client import NFEClient
from app.services.enrichment.nfe_enrichment_service import NFEEnrichmentService
from app.services.extractors.base_extractor import BaseNFEExtractor
from app.services.extractors.extractor_factory import ExtractorFactory
from app.services.nfe_pipeline import NfePipeline
from app.services.normalizers.nfe_normalizer import NfeNormalizer

def build_nfe_data(
    *,
    product_name: str,
    ncm_code: str | None = None,
) -> NFEData:
    """Build NFC-e data used during pipeline tests."""
    market = NFEMarketData(
        cnpj="12345678000190",
        market_name="Market Test",
        market_street="Test Street",
        market_number="100",
        market_district="Downtown",
        market_city="Florianopolis",
        market_state="SC",
    )

    product = NFEProductData(
        product_code="ABC-001",
        code_type="INTERNAL",
        name=product_name,
        unit_price=Decimal("10.00"),
        total_price=Decimal("20.00"),
        quantity=Decimal("2"),
        ncm_code=ncm_code,
        brand=None,
        picture_url=None,
    )

    return NFEData(
        nfe_key="12345678901234567890123456789012345678901234",
        nfe_date=datetime(2026, 7, 23, 10, 0, 0),
        market_data=market,
        products_data=[product],
    )


@pytest.mark.asyncio
async def test_process_executes_pipeline_in_correct_order() -> None:
    """Execute every NFC-e processing stage in the expected order."""

    execution_order: list[str] = []

    extracted_data = build_nfe_data(
        product_name="  COFFEE   500G  ",
    )
    normalized_data = build_nfe_data(
        product_name="COFFEE 500G",
    )
    enriched_data = build_nfe_data(
        product_name="COFFEE 500G",
        ncm_code="09012100",
    )

    async def fetch(url: str) -> str:
        execution_order.append("fetch")
        return "<html></html>"

    def create_extractor() -> BaseNFEExtractor:
        execution_order.append("create_extractor")
        return extractor

    def extract(html: str) -> NFEData:
        execution_order.append("extract")
        return extracted_data

    def normalize(data: NFEData) -> NFEData:
        execution_order.append("normalize")
        assert data is extracted_data
        return normalized_data

    async def enrich(data: NFEData) -> NFEData:
        execution_order.append("enrich")
        assert data is normalized_data
        return enriched_data

    nfe_client = Mock(spec=NFEClient)
    nfe_client.fetch = AsyncMock(side_effect=fetch)

    extractor = Mock(spec=BaseNFEExtractor)
    extractor.extract.side_effect = extract

    extractor_factory = Mock(spec=ExtractorFactory)
    extractor_factory.create.side_effect = create_extractor

    normalizer = Mock(spec=NfeNormalizer)
    normalizer.normalize.side_effect = normalize

    enrichment_service = Mock(spec=NFEEnrichmentService)
    enrichment_service.enrich = AsyncMock(side_effect=enrich)

    pipeline = NfePipeline(
        client=nfe_client,
        extractor_factory=extractor_factory,
        normalizer=normalizer,
        enrichment_service=enrichment_service,
    )

    result = await pipeline.process(
        "https://example.com/nfce",
    )

    assert execution_order == [
        "fetch",
        "create_extractor",
        "extract",
        "normalize",
        "enrich",
    ]
    assert result is enriched_data

@pytest.mark.asyncio
async def test_process_passes_correct_data_between_stages() -> None:
    """Pass the result of each pipeline stage to the next component."""

    html = "<html>NFC-e</html>"

    extracted_data = build_nfe_data(
        product_name="  COFFEE   500G  ",
    )
    normalized_data = build_nfe_data(
        product_name="COFFEE 500G",
    )
    enriched_data = build_nfe_data(
        product_name="COFFEE 500G",
        ncm_code="09012100",
    )

    nfe_client = Mock(spec=NFEClient)
    nfe_client.fetch = AsyncMock(return_value=html)

    extractor = Mock(spec=BaseNFEExtractor)
    extractor.extract.return_value = extracted_data

    extractor_factory = Mock(spec=ExtractorFactory)
    extractor_factory.create.return_value = extractor

    normalizer = Mock(spec=NfeNormalizer)
    normalizer.normalize.return_value = normalized_data

    enrichment_service = Mock(spec=NFEEnrichmentService)
    enrichment_service.enrich = AsyncMock(
        return_value=enriched_data,
    )

    pipeline = NfePipeline(
        client=nfe_client,
        extractor_factory=extractor_factory,
        normalizer=normalizer,
        enrichment_service=enrichment_service,
    )

    qr_code_url = "https://example.com/nfce"

    result = await pipeline.process(qr_code_url)

    nfe_client.fetch.assert_awaited_once_with(qr_code_url)
    extractor_factory.create.assert_called_once_with()
    extractor.extract.assert_called_once_with(html)
    normalizer.normalize.assert_called_once_with(extracted_data)
    enrichment_service.enrich.assert_awaited_once_with(normalized_data)

    assert result is enriched_data