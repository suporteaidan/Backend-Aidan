"""
User API routes.

This module defines HTTP endpoints related to users.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserRead
from app.services.user_services import UserService
from app.db.session import get_async_session

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("", response_model=UserRead, status_code = status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new user.

    - Creates a user
    - Hashes password
    - Creates a default profile
    """
    return await UserService.create_user(db=db, user_in=user_in)