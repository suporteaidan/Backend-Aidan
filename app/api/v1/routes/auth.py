"""Authentication API routes.

This module exposes HTTP endpoints responsible for user authentication.

The login endpoint receives credentials using the OAuth2 password form,
delegates credential validation to AuthenticationService, and creates a
signed JWT access token when authentication succeeds.

The user's email address is received through the OAuth2 ``username`` field.
This preserves compatibility with the OAuth2 password flow while allowing
the application to use email addresses as login identifiers.

Invalid credentials always produce the same HTTP 401 response, preventing
the API from revealing whether an email exists or whether only the password
was incorrect.

Password verification and database queries are delegated to their respective
application layers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_user_repository
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.services.authentication_service import AuthenticationService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

def get_authentication_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthenticationService:
    """Build the authentication service for the current request."""

    return AuthenticationService(
        user_repository=user_repository,
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authentication_service: AuthenticationService = Depends(
        get_authentication_service
    ),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""

    user = await authentication_service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
    )