"""Service responsible for persisting enriched NFC-e data.

This module coordinates the persistence phase of the NFC-e import pipeline.

The service receives an already extracted, normalized, and enriched NFEData
object and converts that application-level representation into persisted
SQLAlchemy entities.

The persistence flow is executed in the following order:

1. Verify whether the NFC-e has already been persisted.
2. Locate or create the issuing Market.
3. Create the NFE associated with the authenticated user and Market.
4. Locate or create each Product in the application catalog.
5. Create a ProductPrice for every product found in the NFC-e.
6. Commit the complete operation as a single database transaction.

The service does not perform HTML parsing, HTTP requests, normalization,
enrichment, or direct SQL queries. Database operations are delegated to
repositories.

All repositories must share the same AsyncSession. This guarantees atomicity:
if any persistence operation fails, the complete NFC-e import is rolled back
and no partial Market, Product, NFE, or ProductPrice data is committed.

Products identified by EAN use their product code as the catalog lookup key.
Products identified by INTERNAL codes use the current MVP strategy based on
the internal product code combined with the normalized product name.

Transaction ownership belongs to this service. Repositories may flush changes
to obtain generated identifiers, but they must never commit independently.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nfe import NFE
from app.models.product import Product, ProductCodeType
from app.repositories.market_repository import MarketRepository
from app.repositories.nfe_repository import NFERepository
from app.repositories.product_price_repository import ProductPriceRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.nfe_data import NFEData, NFEProductData
from app.models.market import Market

class NFEPersistenceService:
    """Coordinate persistence of an enriched NFC-e and its related entities."""

    def __init__(
        self,
        session: AsyncSession,
        market_repository: MarketRepository,
        product_repository: ProductRepository,
        nfe_repository: NFERepository,
        product_price_repository: ProductPriceRepository,
    ) -> None:
        """Initialize the service with a shared session and repositories."""
        self._session = session
        self._market_repository = market_repository
        self._product_repository = product_repository
        self._nfe_repository = nfe_repository
        self._product_price_repository = product_price_repository

    async def persist(
        self,
        nfe_data: NFEData,
        user_id: int,
    ) -> NFE:
        """Persist an enriched NFC-e using a single database transaction."""

        existing_nfe = await self._nfe_repository.get_by_key(
            nfe_data.nfe_key
        )

        if existing_nfe is not None:
            return existing_nfe

        try:
            market = await self._get_or_create_market(nfe_data)

            nfe = await self._nfe_repository.create(
                nfe_key=nfe_data.nfe_key,
                nfe_date=nfe_data.nfe_date,
                market_id=market.id,
                user_id=user_id,
            )

            for product_data in nfe_data.products_data:
                product = await self._get_or_create_product(product_data)

                await self._product_price_repository.create(
                    product_id=product.id,
                    market_id=market.id,
                    nfe_id=nfe.id,
                    unit_price=product_data.unit_price,
                    total_price=product_data.total_price,
                    quantity=product_data.quantity,
                    collected_at=nfe_data.nfe_date,
                )

            await self._session.commit()

            return nfe

        except Exception:
            await self._session.rollback()
            raise

    async def _get_or_create_market(
        self,
        nfe_data: NFEData,
    ) -> Market:
        """Return the existing Market or create it from NFC-e market data."""

        market_data = nfe_data.market_data

        market = await self._market_repository.get_by_cnpj(
            market_data.cnpj
        )

        if market is not None:
            return market

        return await self._market_repository.create(
            cnpj=market_data.cnpj,
            market_name=market_data.market_name,
            market_street=market_data.market_street,
            market_number=market_data.market_number,
            market_district=market_data.market_district,
            market_city=market_data.market_city,
            market_state=market_data.market_state,
        )

    async def _get_or_create_product(
        self,
        product_data: NFEProductData,
    ) -> Product:
        """Return an existing catalog product or create a new one."""

        code_type = ProductCodeType(product_data.code_type)

        if code_type == ProductCodeType.EAN:
            product = await self._product_repository.get_by_ean(
                product_data.product_code
            )
        else:
            product = (
                await self._product_repository.get_internal_by_code_and_name(
                    product_code=product_data.product_code,
                    name=product_data.name,
                )
            )

        if product is not None:
            return product

        return await self._product_repository.create(
            name=product_data.name,
            product_code=product_data.product_code,
            code_type=code_type,
            ncm_code=product_data.ncm_code,
            brand=product_data.brand,
            picture_url=product_data.picture_url,
        )