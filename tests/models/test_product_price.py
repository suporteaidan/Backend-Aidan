"""Tests for the ProductPrice SQLAlchemy model."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market
from app.models.nfe import NFE
from app.models.product import Product, ProductCodeType
from app.models.product_price import ProductPrice
from app.models.profile import Profile
from app.models.user import User

async def create_dependencies(
    db_session: AsyncSession,
) -> tuple[Product, Market, NFE]:
    """Create persisted dependencies required by ProductPrice."""

    profile = Profile()
    db_session.add(profile)
    await db_session.flush()

    user = User(
        profile_id=profile.id,
        name="Product Price User",
        email="product-price@example.com",
        address="Test Address",
        cpf="98765432100",
        password_hash="hashed-password",
        phone="48999999998",
    )
    db_session.add(user)
    await db_session.flush()

    market = Market(
        cnpj="98765432000199",
        market_name="PRICE TEST MARKET",
        market_street="TEST STREET",
        market_number="50",
        market_district="TRINDADE",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )
    db_session.add(market)
    await db_session.flush()

    product = Product(
        name="COFFEE 500G",
        product_code="7891234567890",
        code_type=ProductCodeType.EAN,
        ncm_code="09012100",
    )
    db_session.add(product)
    await db_session.flush()

    nfe = NFE(
        nfe_key="9" * 44,
        user_id=user.id,
        market_id=market.id,
        nfe_date=datetime.now(timezone.utc),
    )
    db_session.add(nfe)
    await db_session.flush()

    return product, market, nfe


@pytest.mark.asyncio
async def test_create_product_price(
    db_session: AsyncSession,
) -> None:
    """Persist a product price associated with its source NFC-e."""

    product, market, nfe = await create_dependencies(db_session)

    collected_at = datetime.now(timezone.utc)

    product_price = ProductPrice(
        product_id=product.id,
        market_id=market.id,
        nfe_id=nfe.id,
        unit_price=Decimal("18.9900"),
        total_price=Decimal("37.98"),
        quantity=Decimal("2.0000"),
        collected_at=collected_at,
    )

    db_session.add(product_price)
    await db_session.flush()
    await db_session.refresh(product_price)

    assert product_price.id is not None
    assert product_price.product_id == product.id
    assert product_price.market_id == market.id
    assert product_price.nfe_id == nfe.id
    assert product_price.unit_price == Decimal("18.9900")
    assert product_price.total_price == Decimal("37.98")
    assert product_price.quantity == Decimal("2.0000")
    assert product_price.collected_at == collected_at.replace(tzinfo=None)
    assert product_price.created_at is not None

@pytest.mark.asyncio
async def test_product_price_allows_zero_unit_price(
    db_session: AsyncSession,
) -> None:
    """Allow zero-valued products such as bonuses or free items."""

    product, market, nfe = await create_dependencies(db_session)

    product_price = ProductPrice(
        product_id=product.id,
        market_id=market.id,
        nfe_id=nfe.id,
        unit_price=Decimal("0.0000"),
        total_price=Decimal("0.00"),
        quantity=Decimal("1.0000"),
        collected_at=datetime.now(timezone.utc),
    )

    db_session.add(product_price)
    await db_session.flush()

    assert product_price.unit_price == Decimal("0.0000")
    assert product_price.total_price == Decimal("0.00")

@pytest.mark.asyncio
async def test_product_price_rejects_negative_unit_price(
    db_session: AsyncSession,
) -> None:
    """Reject negative unit prices."""

    product, market, nfe = await create_dependencies(db_session)

    product_price = ProductPrice(
        product_id=product.id,
        market_id=market.id,
        nfe_id=nfe.id,
        unit_price=Decimal("-1.0000"),
        total_price=Decimal("1.00"),
        quantity=Decimal("1.0000"),
        collected_at=datetime.now(timezone.utc),
    )

    db_session.add(product_price)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_product_price_requires_existing_product(
    db_session: AsyncSession,
) -> None:
    """Reject product prices linked to nonexistent products."""

    _, market, nfe = await create_dependencies(db_session)

    product_price = ProductPrice(
        product_id=999999,
        market_id=market.id,
        nfe_id=nfe.id,
        unit_price=Decimal("10.0000"),
        total_price=Decimal("10.00"),
        quantity=Decimal("1.0000"),
        collected_at=datetime.now(timezone.utc),
    )

    db_session.add(product_price)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_product_price_requires_existing_market(
    db_session: AsyncSession,
) -> None:
    """Reject product prices linked to nonexistent markets."""

    product, _, nfe = await create_dependencies(db_session)

    product_price = ProductPrice(
        product_id=product.id,
        market_id=999999,
        nfe_id=nfe.id,
        unit_price=Decimal("10.0000"),
        total_price=Decimal("10.00"),
        quantity=Decimal("1.0000"),
        collected_at=datetime.now(timezone.utc),
    )

    db_session.add(product_price)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_product_price_requires_existing_nfe(
    db_session: AsyncSession,
) -> None:
    """Reject product prices linked to nonexistent NFC-e documents."""

    product, market, _ = await create_dependencies(db_session)

    product_price = ProductPrice(
        product_id=product.id,
        market_id=market.id,
        nfe_id=999999,
        unit_price=Decimal("10.0000"),
        total_price=Decimal("10.00"),
        quantity=Decimal("1.0000"),
        collected_at=datetime.now(timezone.utc),
    )

    db_session.add(product_price)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()