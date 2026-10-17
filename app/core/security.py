"""Security utilities for authentication and JWT access tokens.

This module centralizes the application's authentication-related security
operations.

Its responsibilities include:

- creating signed JWT access tokens;
- validating and decoding received JWT access tokens;
- defining the signing algorithm used by the application;
- defining the access-token expiration policy.

JWT tokens are signed but not encrypted. For that reason, sensitive
information such as passwords, CPF, or personal data must never be stored
inside the token payload.

The token subject claim (``sub``) is used to identify the authenticated
user. In this application, the user's database identifier is stored as the
subject.

The secret key must be provided through application configuration and must
never be hard-coded or committed to version control.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

password_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
)

ALGORITHM = settings.algorithm

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against its stored hash."""

    return password_context.verify(
        plain_password,
        hashed_password,
    )

def create_access_token(
    *,
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for an authenticated subject."""

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )

def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError:
        raise