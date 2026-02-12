import pytest
from app.services.user_services import UserService
from app.schemas.user import UserCreate
from app.models.profile import ProfileTypeEnum

@pytest.mark.asyncio
async def test_create_user_with_default_profile(db_session):
    user_in = UserCreate(
        name="Ricardo",
        email="test@email.com",
        cpf="12345678900",
        password="123456",
        address=None,
        phone=None,
    )

    user = await UserService.create_user(db_session, user_in)

    assert user.profile is not None
    assert user.profile.id is not None
    assert user.profile.type == ProfileTypeEnum.FREE.value