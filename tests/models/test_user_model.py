from app.models.user import User
import pytest

@pytest.mark.asyncio
async def test_user_creation(db_session):
    user = User(
        name="Ricardo",
        cpf="12345678900",
        email="test@email.com",
        password_hash="hashed",
    )

    assert user.name == "Ricardo"
    assert user.cpf == "12345678900"
    assert user.email == "test@email.com"
