"""Tests for UserRepository database queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_get_by_id_returns_user(
    db_session: AsyncSession,
) -> None:
    """Return the user matching the provided identifier."""

    profile = Profile(
        type="free",
    )

    db_session.add(profile)
    await db_session.flush()

    user = User(
        profile_id=profile.id,
        name="Repository User",
        email="repository@example.com",
        address="Test Address",
        cpf="12345678901",
        password_hash="hashed-password",
        phone="48999999999",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    repository = UserRepository(db_session)

    result = await repository.get_by_id(user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == "repository@example.com"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_user_does_not_exist(
    db_session: AsyncSession,
) -> None:
    """Return None when the identifier does not belong to a user."""

    repository = UserRepository(db_session)

    result = await repository.get_by_id(999999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_returns_user(
    db_session: AsyncSession,
) -> None:
    """Return the user matching the provided email address."""

    profile = Profile(
        type="free",
    )

    db_session.add(profile)
    await db_session.flush()

    user = User(
        profile_id=profile.id,
        name="Email User",
        email="email.repository@example.com",
        address="Test Address",
        cpf="98765432100",
        password_hash="hashed-password",
        phone="48988888888",
    )

    db_session.add(user)
    await db_session.commit()

    repository = UserRepository(db_session)

    result = await repository.get_by_email(
        "email.repository@example.com"
    )

    assert result is not None
    assert result.email == "email.repository@example.com"


@pytest.mark.asyncio
async def test_get_by_email_returns_none_when_user_does_not_exist(
    db_session: AsyncSession,
) -> None:
    """Return None when the email does not belong to a user."""

    repository = UserRepository(db_session)

    result = await repository.get_by_email(
        "missing@example.com"
    )

    assert result is None