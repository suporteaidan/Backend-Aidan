"""Repository for Product database operations.

This module isolates all persistence logic related to the Product model.

The Product entity represents a catalog item and must remain independent
from transactional information such as price, quantity, market, or NFC-e.

The repository is responsible only for querying and creating Product
records. It does not contain business rules, does not perform enrichment,
and does not commit transactions.

Transaction control is intentionally delegated to the service layer so
that Product, Market, NFE, and ProductPrice records can be persisted within
the same atomic database transaction.

The current MVP uses different lookup strategies depending on the product
code type:

- EAN products can be searched by their globally identifiable product code.
- INTERNAL products are not treated as globally unique because the same
  internal code may be reused by different establishments.

More advanced matching strategies for INTERNAL products must remain in the
service layer and must not be implemented directly in this repository.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductCodeType


class ProductRepository:
    """Provide database operations related to Product entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous database session."""
        self._session = session

    async def get_by_ean(self, product_code: str) -> Product | None:
        """Return an EAN product identified by its product code."""

        statement = select(Product).where(
            Product.product_code == product_code,
            Product.code_type == ProductCodeType.EAN,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_internal_by_code_and_name(
        self,
        product_code: str,
        name: str,
    ) -> Product | None:
        """Return an internal product matching its code and normalized name."""

        statement = select(Product).where(
            Product.product_code == product_code,
            Product.code_type == ProductCodeType.INTERNAL,
            Product.name == name,
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        name: str,
        product_code: str,
        code_type: ProductCodeType,
        description: str | None = None,
        ncm_code: str | None = None,
        brand: str | None = None,
        picture_url: str | None = None,
    ) -> Product:
        """Create and stage a new catalog product in the current transaction."""

        product = Product(
            name=name,
            description=description,
            product_code=product_code,
            code_type=code_type,
            ncm_code=ncm_code,
            brand=brand,
            picture_url=picture_url,
        )

        self._session.add(product)
        await self._session.flush()

        return product