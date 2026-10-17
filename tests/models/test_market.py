"""Tests for the Market SQLAlchemy model."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market

@pytest.mark.asyncio
async def test_create_market(
    db_session: AsyncSession,
) -> None:
    """Persist a market with normalized business and address data."""

    market = Market(
        cnpj="12345678000190",
        market_name="SUPERMARKET EXAMPLE",
        market_street="MAIN STREET",
        market_number="100",
        market_district="DOWNTOWN",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )

    db_session.add(market)
    await db_session.flush()
    await db_session.refresh(market)

    assert market.id is not None
    assert market.cnpj == "12345678000190"
    assert market.market_name == "SUPERMARKET EXAMPLE"
    assert market.market_street == "MAIN STREET"
    assert market.market_number == "100"
    assert market.market_district == "DOWNTOWN"
    assert market.market_city == "FLORIANOPOLIS"
    assert market.market_state == "SC"
    assert market.created_at is not None
    assert market.updated_at is not None

@pytest.mark.asyncio
async def test_market_can_be_retrieved_by_cnpj(
    db_session: AsyncSession,
) -> None:
    """Retrieve a persisted market by its CNPJ."""

    market = Market(
        cnpj="12345678000192",
        market_name="TEST MARKET",
        market_street="TEST STREET",
        market_number="10",
        market_district="TRINDADE",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )

    db_session.add(market)
    await db_session.flush()

    result = await db_session.execute(
        select(Market).where(Market.cnpj == market.cnpj)
    )
    stored_market = result.scalar_one()

    assert stored_market.id == market.id
    assert stored_market.cnpj == "12345678000192"

@pytest.mark.asyncio
async def test_market_cnpj_must_be_unique(
    db_session: AsyncSession,
) -> None:
    """Reject duplicated market CNPJ values."""

    first_market = Market(
        cnpj="12345678000193",
        market_name="FIRST MARKET",
        market_street="FIRST STREET",
        market_number="1",
        market_district="CENTER",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )

    second_market = Market(
        cnpj="12345678000193",
        market_name="SECOND MARKET",
        market_street="SECOND STREET",
        market_number="2",
        market_district="CENTER",
        market_city="FLORIANOPOLIS",
        market_state="SC",
    )

    db_session.add(first_market)
    await db_session.flush()

    db_session.add(second_market)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()