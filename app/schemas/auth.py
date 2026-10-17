"""Pydantic schemas used by the authentication API.

This module defines the response contract returned after successful user
authentication.

Login credentials are received through the OAuth2 password form handled by
FastAPI, so a dedicated Pydantic request schema is not required.

The authentication response contains the JWT access token and its token type,
allowing clients to authenticate subsequent requests using the HTTP
Authorization header.
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Represent the access token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"