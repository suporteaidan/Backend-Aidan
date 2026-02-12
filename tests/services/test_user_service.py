import pytest
from unittest.mock import patch

from app.schemas.user import UserCreate
from app.services.user_services import UserService
from sqlalchemy.exc import IntegrityError

from app.models.profile import Profile
from sqlalchemy.future import select

@pytest.mark.asyncio
@patch("app.services.user_services.hash_password", return_value="hashed_password")
async def test_create_user(mock_hash_password, db_session):
    mock_hash_password.return_value = "hashed_password"

    user_in = UserCreate(
        name="Ricardo",
        cpf="12345678900",
        email="ricardo@email.com",
        password="123456",
    )

    user = await UserService.create_user(
        db=db_session,
        user_in=user_in,
    )

    assert user.id is not None
    assert user.email == "ricardo@email.com"
    assert user.password_hash == "hashed_password"

@pytest.mark.asyncio
@patch("app.services.user_services.hash_password", return_value="hashed_password")
async def test_create_user_with_duplicate_cpf(mock_hash_password, db_session):
    user_1 = UserCreate(
        name="Ricardo",
        cpf="12345678900",
        email="ricardo@email.com",
        password="123456",
    )

    user_2 = UserCreate(
        name="Ana",
        cpf="12345678900",  # CPF duplicate
        email="ana@email.com",
        password="654321",
    )

    await UserService.create_user(
        db=db_session,
        user_in=user_1,
    )

    with pytest.raises(IntegrityError):
        await UserService.create_user(
            db=db_session,
            user_in=user_2,
        )

@pytest.mark.asyncio
@patch("app.services.user_services.hash_password", return_value="hashed_password")
async def test_transaction_rollback_on_user_creation_error(mock_hash_password,db_session):

    user_1 = UserCreate(
        name="Ricardo",
        cpf="12345678900",
        email="duplicado@email.com",
        password="123456",
    )

    user_2 = UserCreate(
        name="Ana",
        cpf="09876543211",
        email="duplicado@email.com", # email duplicate
        password="654321",
    )

    # Create the first user
    await UserService.create_user(
        db=db_session,  
        user_in=user_1,
    )

    # Check number of profiles before attempting to create the second user
    result_before = await db_session.execute(select(Profile))
    profiles_before = result_before.scalars().all()
    count_before = len(profiles_before)

    # try to create the second one with the same email
    with pytest.raises(IntegrityError):
        await UserService.create_user(
            db=db_session,
            user_in=user_2,
        )

    # Check number of profiles after the failed creation
    result_after = await db_session.execute(select(Profile))
    profiles_after = result_after.scalars().all()
    count_after = len(profiles_after)

    # Ensure no new profile was created
    assert count_before == count_after

