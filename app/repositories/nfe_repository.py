"""Repository for NFE database operations.

This module centralizes persistence operations related to imported NFC-e
documents.

The NFE entity stores the fiscal document identity and its associations
with the user that imported it and the market that issued it.

The repository is intentionally limited to database access responsibilities.
It does not fetch NFC-e pages, extract HTML, normalize data, enrich products,
or decide how duplicated NFC-e documents should be handled.

Business decisions such as whether an existing NFC-e should be returned,
rejected, or skipped belong to the service layer.

The repository does not execute commits. This allows the complete NFC-e
persistence flow to remain atomic together with Market, Product, and
ProductPrice operations.

The user relationship is optional because an imported NFC-e must remain
stored even if the user account is later deleted. The database foreign key
uses ON DELETE SET NULL for that behavior.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nfe import NFE


class NFERepository:
    """Provide database operations related to NFE entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous database session."""
        self._session = session

    async def get_by_key(self, nfe_key: str) -> NFE | None:
        """Return an NFC-e identified by its unique access key."""

        statement = select(NFE).where(NFE.nfe_key == nfe_key)

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        nfe_key: str,
        nfe_date: datetime,
        market_id: int,
        user_id: int | None,
    ) -> NFE:
        """Create and stage an NFC-e record in the current transaction."""

        nfe = NFE(
            nfe_key=nfe_key,
            nfe_date=nfe_date,
            market_id=market_id,
            user_id=user_id,
        )

        self._session.add(nfe)
        await self._session.flush()

        return nfe