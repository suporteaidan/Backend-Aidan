"""
test for UserRead schema to ensure password fields are not exposed
"""


import pytest
from app.schemas.user import UserRead
from app.models.user import User

def test_user_read_does_not_expose_password():
    user = User(
        name="Ricardo",
        email="ricardo@email.com",
        cpf="12345678900",
        password_hash="hashed_password",
    )

    user_read =UserRead.model_validate(user)

    data = user_read.model_dump()

    assert "password" not in data
    assert "password_hash" not in data