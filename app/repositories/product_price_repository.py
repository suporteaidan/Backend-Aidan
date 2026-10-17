"""Repository for ProductPrice database operations.

This module contains persistence logic for prices collected from imported
NFC-e documents.

ProductPrice represents transactional information and connects a catalog
Product with the Market and NFE from which the price was obtained.

The entity stores values that vary between purchases, including unit price,
total price, quantity, and collection date. These values intentionally do
not belong to the Product catalog itself.

This repository only creates and queries ProductPrice records. It does not
decide which Product should be reused, which Market should be associated
with an NFC-e, or whether a fiscal document is duplicated.

Transaction management remains outside this repository. No commit is
performed here so that all ProductPrice records belonging to one NFC-e can
be persisted atomically with the related Market, Product, and NFE records.

Database constraints remain responsible for protecting invalid values such
as negative prices or non-positive quantities.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_price import ProductPrice


class ProductPriceRepository:
    """Provide database operations related to ProductPrice entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous database session."""
        self._session = session

    async def create(
        self,
        *,
        product_id: int,
        market_id: int,
        nfe_id: int,
        unit_price: Decimal,
        total_price: Decimal,
        quantity: Decimal,
        collected_at: datetime,
    ) -> ProductPrice:
        """Create and stage a product price in the current transaction."""

        product_price = ProductPrice(
            product_id=product_id,
            market_id=market_id,
            nfe_id=nfe_id,
            unit_price=unit_price,
            total_price=total_price,
            quantity=quantity,
            collected_at=collected_at,
        )

        self._session.add(product_price)
        await self._session.flush()

        return product_price

    async def list_by_nfe_id(
        self,
        nfe_id: int,
    ) -> list[ProductPrice]:
        """Return all product prices associated with an NFC-e."""

        statement = select(ProductPrice).where(
            ProductPrice.nfe_id == nfe_id
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())