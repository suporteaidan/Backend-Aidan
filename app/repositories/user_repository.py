"""Repository for User database query operations.

This module centralizes database access related to User entities.

The repository provides reusable persistence operations without containing
authentication, authorization, password validation, or JWT-specific business
rules.

For the authentication flow, users need to be retrieved in two different
situations:

- by email during credential authentication;
- by database identifier when resolving the authenticated user from the
    subject stored in a JWT access token.

The repository receives an AsyncSession through dependency injection and
does not create or manage database sessions independently.

Transaction management also remains outside this repository. Query operations
performed here participate in the transaction associated with the injected
session.

Keeping database access isolated in repositories prevents authentication
services and FastAPI dependencies from containing direct SQLAlchemy queries
and improves testability and separation of concerns.
"""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

class UserRepository:
    """Provide database query operations related to User entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous database session."""

        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Return a user identified by its database identifier."""

        statement = select(User).where(
            User.id == user_id
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Return a user identified by its email address."""

        statement = select(User).where(
            User.email == email
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()