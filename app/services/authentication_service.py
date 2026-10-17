"""Service responsible for authenticating application users.

This module contains the business logic required to validate user credentials
during the login process.

Authentication is intentionally separated from the HTTP layer, JWT utilities,
and database access implementation.

The service coordinates two operations:

1. Retrieve the user by email through UserRepository.
2. Verify the provided plain-text password against the stored password hash.

If either the user does not exist or the password is invalid, authentication
fails and the service returns None.

The service does not reveal which credential was incorrect. This allows the
HTTP layer to return a generic authentication error and avoids exposing
whether a given email address exists in the system.

JWT creation is not performed here. Token generation belongs to the security
layer and is executed only after credentials have been successfully
authenticated.
"""

from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository

class AuthenticationService:
    """Authenticate users using their email address and password."""

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Initialize the service with a user repository."""

        self._user_repository = user_repository

    async def authenticate(
        self,
        *,
        email: str,
        password: str,
    ) -> User | None:
        """Return the authenticated user when credentials are valid."""

        user = await self._user_repository.get_by_email(email)

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user