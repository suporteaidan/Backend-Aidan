"""FastAPI dependencies for authenticated user resolution.

This module connects the application's JWT security utilities with FastAPI's
request dependency system.

Its main responsibility is resolving the currently authenticated User from
the Bearer access token sent in the HTTP Authorization header.

The authentication flow is:

Authorization header
    ↓
OAuth2PasswordBearer
    ↓
JWT access token
    ↓
decode_access_token()
    ↓
"sub" claim
    ↓
user_id
    ↓
UserRepository.get_by_id()
    ↓
authenticated User

The JWT stores only the user identifier as its subject. User information is
loaded from the database for each authenticated request so that the database
remains the authoritative source of user data.

This module does not authenticate email/password credentials and does not
create access tokens. Those responsibilities belong to the login flow and
security layer respectively.

Invalid, expired, malformed, or otherwise unusable tokens result in an
HTTP 401 Unauthorized response.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    """Build the user repository using the request database session."""

    return UserRepository(session)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Return the user authenticated by the provided JWT access token."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user