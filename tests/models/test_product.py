"""Tests for the Product SQLAlchemy model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductCodeType

@pytest.mark.asyncio
async def test_create_ean_product(
    db_session: AsyncSession,
) -> None:
    """Persist a product identified by an EAN code."""

    product = Product(
        name="COFFEE 500G",
        description="Roasted and ground coffee",
        product_code="7891234567890",
        code_type=ProductCodeType.EAN,
        ncm_code="09012100",
        brand="Example Brand",
        picture_url="https://example.com/coffee.jpg",
    )

    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)

    assert product.id is not None
    assert product.name == "COFFEE 500G"
    assert product.product_code == "7891234567890"
    assert product.code_type == ProductCodeType.EAN
    assert product.ncm_code == "09012100"
    assert product.brand == "Example Brand"
    assert product.picture_url == "https://example.com/coffee.jpg"
    assert product.created_at is not None
    assert product.updated_at is not None

@pytest.mark.asyncio
async def test_create_internal_product(
    db_session: AsyncSession,
) -> None:
    """Persist a product identified by an internal market code."""

    product = Product(
        name="WHITE RICE 1KG",
        product_code="ABC-001",
        code_type=ProductCodeType.INTERNAL,
    )

    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)

    assert product.id is not None
    assert product.product_code == "ABC-001"
    assert product.code_type == ProductCodeType.INTERNAL
    assert product.description is None
    assert product.ncm_code is None
    assert product.brand is None
    assert product.picture_url is None

@pytest.mark.asyncio
async def test_product_can_be_retrieved(
    db_session: AsyncSession,
) -> None:
    """Retrieve a persisted product by its identifier."""

    product = Product(
        name="WHOLE MILK 1L",
        product_code="7891234567005",
        code_type=ProductCodeType.EAN,
    )

    db_session.add(product)
    await db_session.flush()

    result = await db_session.execute(
        select(Product).where(Product.id == product.id)
    )
    stored_product = result.scalar_one()

    assert stored_product.id == product.id
    assert stored_product.name == "WHOLE MILK 1L"
    assert stored_product.product_code == "7891234567005"

@pytest.mark.asyncio
async def test_product_does_not_store_price_and_quantity(
    db_session: AsyncSession,
) -> None:
    """Confirm that the product catalog does not store price data."""

    product = Product(
        name="BEANS 1KG",
        product_code="7891234567012",
        code_type=ProductCodeType.EAN,
    )

    db_session.add(product)
    await db_session.flush()

    assert not hasattr(product, "unit_price")
    assert not hasattr(product, "total_price")
    assert not hasattr(product, "quantity")