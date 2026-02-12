"""
User service module.

This module contains all business logic related to users.
It is responsible for creating users, handling password hashing,
and managing user-profile relationships.
"""
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.security.password import hash_password
from app.models.profile import Profile, ProfileTypeEnum
from sqlalchemy.exc import IntegrityError


class UserService:
    """
    Service layer for user-related operations.
    """

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_in: UserCreate
    ) -> User:
        try:
            """
            Create a new user with an associated profile.

            Args:
                db (AsyncSession): Database session.
                user_in (UserCreate): User creation data.

            Returns:
                User: The created user instance.
            """

            # Hash the user's password
            hashed_password = hash_password(user_in.password)

            #create Profile
            profile = Profile(
                type = ProfileTypeEnum.FREE.value
            )

            # Create the user 
            user = User(
                name = user_in.name,
                cpf = user_in.cpf,
                email = user_in.email,
                address = user_in.address,
                phone = user_in.phone,
                password_hash = hashed_password,
                profile = profile
            )

            # Persist data
            db.add(user)
            await db.commit()
            await db.refresh(user, attribute_names=["profile"])

            return user
    
        except IntegrityError:
            await db.rollback()
            raise