"""FastAPI dependencies for the NFC-e processing flow.

This module centralizes the construction and composition of all services
required by the NFC-e import feature.

The dependency graph includes two main branches:

Persistence branch:
    AsyncSession
        ↓
    Repositories
        ↓
    NFEPersistenceService

Enrichment branch:
    httpx.AsyncClient
        ↓
    BrasilApiNcmClient
        ↓
    NFEEnrichmentService

Pipeline branch:
    NFEClient
    ExtractorFactory
    NfeNormalizer
    NFEEnrichmentService
    NFEPersistenceService
        ↓
    NfePipeline

The external HTTP client is created and closed through a FastAPI dependency
using yield. This guarantees proper resource cleanup after each request.

All persistence repositories share the same AsyncSession so that the complete
NFC-e persistence process can be committed or rolled back atomically.

Keeping dependency composition in this module prevents API endpoints from
being responsible for creating infrastructure objects and application
services directly.
"""

from collections.abc import AsyncGenerator
from app.services.clients.brasil_api_ncm_client import BrasilApiNcmClient
import httpx

from app.services.clients.base_ncm_client import BaseNCMClient
from app.services.clients.nfe_client import NFEClient
from app.services.enrichment.nfe_enrichment_service import NFEEnrichmentService
from app.services.extractors.extractor_factory import ExtractorFactory
from app.services.nfe_pipeline import NfePipeline
from app.services.normalizers.nfe_normalizer import NfeNormalizer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.repositories.market_repository import MarketRepository
from app.repositories.nfe_repository import NFERepository
from app.repositories.product_price_repository import ProductPriceRepository
from app.repositories.product_repository import ProductRepository
from app.services.persistence.nfe_persistence_service import (
    NFEPersistenceService,
)


async def get_external_http_client() -> AsyncGenerator[
    httpx.AsyncClient,
    None,
]:
    """Provide an asynchronous HTTP client for external integrations."""

    async with httpx.AsyncClient() as client:
        yield client


def get_nfe_client() -> NFEClient:
    """Build the client responsible for retrieving public NFC-e content."""

    return NFEClient()


def get_extractor_factory() -> ExtractorFactory:
    """Build the factory responsible for selecting NFC-e extractors."""

    return ExtractorFactory()


def get_nfe_normalizer() -> NfeNormalizer:
    """Build the service responsible for normalizing extracted NFC-e data."""

    return NfeNormalizer()


def get_brasil_api_ncm_client(
    client: httpx.AsyncClient = Depends(get_external_http_client),
) -> BrasilApiNcmClient:
    """Build the BrasilAPI client used for NCM searches."""

    return BrasilApiNcmClient(client=client)


def get_nfe_enrichment_service(ncm_cliente: BaseNCMClient = Depends(get_brasil_api_ncm_client)) -> NFEEnrichmentService:
    """Build the service responsible for enriching NFC-e product data."""

    return NFEEnrichmentService(ncm_client=ncm_cliente)

def get_nfe_persistence_service(
    session: AsyncSession = Depends(get_async_session),
) -> NFEPersistenceService:
    """Build the NFC-e persistence service using one database session."""

    market_repository = MarketRepository(session)
    product_repository = ProductRepository(session)
    nfe_repository = NFERepository(session)
    product_price_repository = ProductPriceRepository(session)

    return NFEPersistenceService(
        session=session,
        market_repository=market_repository,
        product_repository=product_repository,
        nfe_repository=nfe_repository,
        product_price_repository=product_price_repository,
    )

def get_nfe_pipeline(
    client: NFEClient = Depends(get_nfe_client),
    extractor_factory: ExtractorFactory = Depends(
        get_extractor_factory
    ),
    normalizer: NfeNormalizer = Depends(get_nfe_normalizer),
    enrichment_service: NFEEnrichmentService = Depends(
        get_nfe_enrichment_service
    ),
    persistence_service: NFEPersistenceService = Depends(
        get_nfe_persistence_service
    ),
) -> NfePipeline:
    """Build the complete NFC-e processing pipeline."""

    return NfePipeline(
        client=client,
        extractor_factory=extractor_factory,
        normalizer=normalizer,
        enrichment_service=enrichment_service,
        persistence_service=persistence_service,
    )