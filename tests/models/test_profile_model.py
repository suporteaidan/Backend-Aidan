from app.models.profile import Profile, ProfileTypeEnum
import pytest

@pytest.mark.asyncio
async def test_profile_defaults(db_session):
    profile = Profile()

    db_session.add(profile)
    await db_session.commit() 
    await db_session.refresh(profile)

    assert profile.type == ProfileTypeEnum.FREE.value
    assert profile.photo is None
