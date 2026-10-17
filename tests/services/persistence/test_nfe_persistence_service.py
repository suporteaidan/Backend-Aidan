"""Tests for the NFE persistence service."""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market
from app.models.nfe import NFE
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.profile import Profile
from app.models.user import User
from app.repositories.market_repository import MarketRepository
from app.repositories.nfe_repository import NFERepository
from app.repositories.product_price_repository import ProductPriceRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.nfe_data import NFEData, NFEMarketData, NFEProductData
from app.services.persistence.nfe_persistence_service import (
    NFEPersistenceService,
)

async def create_user(db_session: AsyncSession) -> User:
    """Create and persist a user required by persistence tests."""

    profile = Profile()
    db_session.add(profile)
    await db_session.flush()

    user = User(
        profile_id=profile.id,
        name="Persistence User",
        email="persistence@example.com",
        address="Test Address",
        cpf="12345678901",
        password_hash="hashed-password",
        phone="48999999999",
    )

    db_session.add(user)
    await db_session.flush()

    return user

def create_nfe_data(
    *,
    nfe_key: str = "1" * 44,
) -> NFEData:
    """Create normalized and enriched NFC-e data for persistence tests."""

    return NFEData(
        nfe_key=nfe_key,
        nfe_date=datetime(2026, 8, 18, 10, 0, 0),
        market_data=NFEMarketData(
            cnpj="12345678000190",
            market_name="TEST MARKET",
            market_street="TEST STREET",
            market_number="100",
            market_district="TRINDADE",
            market_city="FLORIANOPOLIS",
            market_state="SC",
        ),
        products_data=[
            NFEProductData(
                product_code="7891234567890",
                code_type="EAN",
                name="COFFEE 500G",
                unit_price=Decimal("18.9900"),
                total_price=Decimal("37.98"),
                quantity=Decimal("2.0000"),
                ncm_code="09012100",
                brand="TEST BRAND",
                picture_url=None,
            ),
            NFEProductData(
                product_code="ABC-001",
                code_type="INTERNAL",
                name="FRENCH BREAD",
                unit_price=Decimal("15.9000"),
                total_price=Decimal("7.95"),
                quantity=Decimal("0.5000"),
                ncm_code="19059090",
                brand=None,
                picture_url=None,
            ),
        ],
    )


def create_service(
    db_session: AsyncSession,
) -> NFEPersistenceService:
    """Create the persistence service and repositories using one session."""

    return NFEPersistenceService(
        session=db_session,
        market_repository=MarketRepository(db_session),
        product_repository=ProductRepository(db_session),
        nfe_repository=NFERepository(db_session),
        product_price_repository=ProductPriceRepository(db_session),
    )

@pytest.mark.asyncio
async def test_persist_nfe(
    db_session: AsyncSession,
) -> None:
    """Persist the complete NFC-e graph."""

    user = await create_user(db_session)
    nfe_data = create_nfe_data()
    service = create_service(db_session)

    nfe = await service.persist(
        nfe_data=nfe_data,
        user_id=user.id,
    )

    assert nfe.id is not None
    assert nfe.nfe_key == nfe_data.nfe_key
    assert nfe.user_id == user.id
    assert nfe.market_id is not None

    market_count = await db_session.scalar(
        select(func.count()).select_from(Market)
    )
    product_count = await db_session.scalar(
        select(func.count()).select_from(Product)
    )
    nfe_count = await db_session.scalar(
        select(func.count()).select_from(NFE)
    )
    product_price_count = await db_session.scalar(
        select(func.count()).select_from(ProductPrice)
    )

    assert market_count == 1
    assert product_count == 2
    assert nfe_count == 1
    assert product_price_count == 2


@pytest.mark.asyncio
async def test_persist_reuses_existing_market(
    db_session: AsyncSession,
) -> None:
    """Reuse a market when another NFC-e has the same CNPJ."""

    user = await create_user(db_session)
    service = create_service(db_session)

    first_data = create_nfe_data(
        nfe_key="2" * 44,
    )
    second_data = create_nfe_data(
        nfe_key="3" * 44,
    )

    first_nfe = await service.persist(
        nfe_data=first_data,
        user_id=user.id,
    )
    second_nfe = await service.persist(
        nfe_data=second_data,
        user_id=user.id,
    )

    market_count = await db_session.scalar(
        select(func.count()).select_from(Market)
    )

    assert market_count == 1
    assert first_nfe.market_id == second_nfe.market_id


@pytest.mark.asyncio
async def test_persist_reuses_existing_products(
    db_session: AsyncSession,
) -> None:
    """Reuse catalog products across different NFC-e documents."""

    user = await create_user(db_session)
    service = create_service(db_session)

    await service.persist(
        nfe_data=create_nfe_data(nfe_key="4" * 44),
        user_id=user.id,
    )

    await service.persist(
        nfe_data=create_nfe_data(nfe_key="5" * 44),
        user_id=user.id,
    )

    product_count = await db_session.scalar(
        select(func.count()).select_from(Product)
    )
    product_price_count = await db_session.scalar(
        select(func.count()).select_from(ProductPrice)
    )

    assert product_count == 2
    assert product_price_count == 4


@pytest.mark.asyncio
async def test_persist_same_nfe_is_idempotent(
    db_session: AsyncSession,
) -> None:
    """Avoid duplicating an NFC-e and its product prices."""

    user = await create_user(db_session)
    service = create_service(db_session)
    nfe_data = create_nfe_data(
        nfe_key="6" * 44,
    )

    first_nfe = await service.persist(
        nfe_data=nfe_data,
        user_id=user.id,
    )
    second_nfe = await service.persist(
        nfe_data=nfe_data,
        user_id=user.id,
    )

    nfe_count = await db_session.scalar(
        select(func.count()).select_from(NFE)
    )
    product_price_count = await db_session.scalar(
        select(func.count()).select_from(ProductPrice)
    )

    assert first_nfe.id == second_nfe.id
    assert nfe_count == 1
    assert product_price_count == 2

@pytest.mark.asyncio
async def test_persist_creates_ean_product_with_enrichment(
    db_session: AsyncSession,
) -> None:
    """Persist enrichment information available for a product."""

    user = await create_user(db_session)
    service = create_service(db_session)

    await service.persist(
        nfe_data=create_nfe_data(nfe_key="7" * 44),
        user_id=user.id,
    )

    result = await db_session.execute(
        select(Product).where(
            Product.product_code == "7891234567890"
        )
    )
    product = result.scalar_one()

    assert product.ncm_code == "09012100"
    assert product.brand == "TEST BRAND"
    assert product.picture_url is None


@pytest.mark.asyncio
async def test_persist_creates_internal_product(
    db_session: AsyncSession,
) -> None:
    """Persist a product identified by an internal market code."""

    user = await create_user(db_session)
    service = create_service(db_session)

    await service.persist(
        nfe_data=create_nfe_data(nfe_key="8" * 44),
        user_id=user.id,
    )

    result = await db_session.execute(
        select(Product).where(
            Product.product_code == "ABC-001"
        )
    )
    product = result.scalar_one()

    assert product.name == "FRENCH BREAD"
    assert product.code_type.value == "INTERNAL"
    assert product.ncm_code == "19059090"


@pytest.mark.asyncio
async def test_persist_product_prices_use_nfe_date(
    db_session: AsyncSession,
) -> None:
    """Use the NFC-e issue date as the price collection date."""

    user = await create_user(db_session)
    service = create_service(db_session)
    nfe_data = create_nfe_data(
        nfe_key="9" * 44,
    )

    nfe = await service.persist(
        nfe_data=nfe_data,
        user_id=user.id,
    )

    result = await db_session.execute(
        select(ProductPrice).where(
            ProductPrice.nfe_id == nfe.id
        )
    )
    prices = list(result.scalars().all())

    assert len(prices) == 2

    for price in prices:
        assert price.collected_at == nfe_data.nfe_date


@pytest.mark.asyncio
async def test_persist_rolls_back_on_error(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rollback the complete NFC-e persistence when a price fails."""

    user = await create_user(db_session)

    market_repository = MarketRepository(db_session)
    product_repository = ProductRepository(db_session)
    nfe_repository = NFERepository(db_session)
    product_price_repository = ProductPriceRepository(db_session)

    service = NFEPersistenceService(
        session=db_session,
        market_repository=market_repository,
        product_repository=product_repository,
        nfe_repository=nfe_repository,
        product_price_repository=product_price_repository,
    )

    async def failing_create(**kwargs: object) -> None:
        raise RuntimeError("Simulated persistence failure")

    monkeypatch.setattr(
        product_price_repository,
        "create",
        failing_create,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated persistence failure",
    ):
        await service.persist(
            nfe_data=create_nfe_data(nfe_key="1" * 43 + "0"),
            user_id=user.id,
        )

    market_count = await db_session.scalar(
        select(func.count()).select_from(Market)
    )
    product_count = await db_session.scalar(
        select(func.count()).select_from(Product)
    )
    nfe_count = await db_session.scalar(
        select(func.count()).select_from(NFE)
    )
    product_price_count = await db_session.scalar(
        select(func.count()).select_from(ProductPrice)
    )

    assert market_count == 0
    assert product_count == 0
    assert nfe_count == 0
    assert product_price_count == 0