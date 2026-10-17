"""Tests for the NFE SQLAlchemy model."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market
from app.models.nfe import NFE
from app.models.profile import Profile
from app.models.user import User

async def create_user(db_session: AsyncSession) -> User:
    """Create a persisted user for NFE tests."""

    profile = Profile()

    db_session.add(profile)
    await db_session.flush()

    user = User(
        profile_id=profile.id,
        name="Test User",
        email="nfe-user@example.com",
        address="Test Address",
        cpf="12345678901",
        password_hash="hashed-password",
        phone="48999999999",
    )

    db_session.add(user)
    await db_session.flush()

    return user

async def create_market(db_session: AsyncSession) -> Market:
    """Create a persisted market for NFE tests."""

    market = Market(
        cnpj="12345678000190",
        market_name="TEST MARKET",
        market_street="TEST STREET",
        market_number="100",
        market_district="TRINDADE",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )

    db_session.add(market)
    await db_session.flush()

    return market

@pytest.mark.asyncio
async def test_create_nfe(
    db_session: AsyncSession,
) -> None:
    """Persist an NFC-e linked to a user and market."""

    user = await create_user(db_session)
    market = await create_market(db_session)

    nfe_date = datetime(
        2026,
        8,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    nfe = NFE(
        nfe_key="1" * 44,
        user_id=user.id,
        market_id=market.id,
        nfe_date=nfe_date,
    )

    db_session.add(nfe)
    await db_session.flush()
    await db_session.refresh(nfe)

    assert nfe.id is not None
    assert nfe.nfe_key == "1" * 44
    assert nfe.user_id == user.id
    assert nfe.market_id == market.id
    assert nfe.nfe_date == nfe_date.replace(tzinfo=None)
    assert nfe.created_at is not None

@pytest.mark.asyncio
async def test_nfe_can_be_retrieved_by_key(
    db_session: AsyncSession,
) -> None:
    """Retrieve a persisted NFC-e by its access key."""

    user = await create_user(db_session)
    market = await create_market(db_session)

    nfe = NFE(
        nfe_key="2" * 44,
        user_id=user.id,
        market_id=market.id,
        nfe_date=datetime.now(timezone.utc),
    )

    db_session.add(nfe)
    await db_session.flush()

    result = await db_session.execute(
        select(NFE).where(NFE.nfe_key == nfe.nfe_key)
    )
    stored_nfe = result.scalar_one()

    assert stored_nfe.id == nfe.id
    assert stored_nfe.nfe_key == "2" * 44
    assert stored_nfe.user_id == user.id
    assert stored_nfe.market_id == market.id

@pytest.mark.asyncio
async def test_nfe_key_must_be_unique(
    db_session: AsyncSession,
) -> None:
    """Reject duplicated NFC-e access keys."""

    user = await create_user(db_session)
    market = await create_market(db_session)

    nfe_key = "3" * 44

    first_nfe = NFE(
        nfe_key=nfe_key,
        user_id=user.id,
        market_id=market.id,
        nfe_date=datetime.now(timezone.utc),
    )

    db_session.add(first_nfe)
    await db_session.flush()

    second_nfe = NFE(
        nfe_key=nfe_key,
        user_id=user.id,
        market_id=market.id,
        nfe_date=datetime.now(timezone.utc),
    )

    db_session.add(second_nfe)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_nfe_requires_existing_user(
    db_session: AsyncSession,
) -> None:
    """Reject an NFC-e linked to a nonexistent user."""

    market = await create_market(db_session)

    nfe = NFE(
        nfe_key="4" * 44,
        user_id=999999,
        market_id=market.id,
        nfe_date=datetime.now(timezone.utc),
    )

    db_session.add(nfe)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()

@pytest.mark.asyncio
async def test_nfe_requires_existing_market(
    db_session: AsyncSession,
) -> None:
    """Reject an NFC-e linked to a nonexistent market."""

    user = await create_user(db_session)

    nfe = NFE(
        nfe_key="5" * 44,
        user_id=user.id,
        market_id=999999,
        nfe_date=datetime.now(timezone.utc),
    )

    db_session.add(nfe)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()