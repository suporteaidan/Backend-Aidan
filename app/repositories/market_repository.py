"""
Repository for Market persistence operations.

This module defines the data access layer responsible for interacting
with Market records in the database.

The MarketRepository encapsulates SQLAlchemy queries and persistence
operations related to the Market entity, keeping database-specific
logic separated from the application's business rules.

Responsibilities
----------------
- Retrieve markets using domain identifiers such as CNPJ.
- Create and stage new Market entities in the current database transaction.
- Execute asynchronous database operations using SQLAlchemy AsyncSession.
- Keep query and persistence logic isolated from service and API layers.

Transaction Management
----------------------
The repository does not commit transactions directly.

Methods such as ``create`` use ``flush()`` to synchronize pending
changes with the database while keeping the transaction open. This
allows higher-level services to coordinate multiple database operations
and decide whether the transaction should be committed or rolled back.

Architecture
------------
Typical application flow:

    API / Router
        ↓
    Service
        ↓
    Repository
        ↓
    SQLAlchemy
        ↓
    Database

By centralizing database access in repositories, the application gains
better separation of concerns, lower coupling between business logic
and persistence technology, improved testability, and reusable queries.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market import Market


class MarketRepository:
    """Provide database operations related to Market entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous database session."""
        self._session = session

    async def get_by_cnpj(self, cnpj: str) -> Market | None:
        """Return a market identified by its CNPJ, if it exists."""

        statement = select(Market).where(Market.cnpj == cnpj)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        cnpj: str,
        market_name: str,
        market_street: str,
        market_number: str,
        market_district: str,
        market_city: str,
        market_state: str | None,
    ) -> Market:
        """Create and stage a new market in the current transaction."""

        market = Market(
            cnpj=cnpj,
            market_name=market_name,
            market_street=market_street,
            market_number=market_number,
            market_district=market_district,
            market_city=market_city,
            market_state=market_state,
        )

        self._session.add(market)
        await self._session.flush()

        return market