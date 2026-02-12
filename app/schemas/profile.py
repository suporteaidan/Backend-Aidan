from datetime import datetime
from app.models.profile import ProfileTypeEnum
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class ProfileBase(BaseModel):
    type: ProfileTypeEnum = ProfileTypeEnum.FREE    

class ProfileCreate(ProfileBase):
    photo: str | None = None

class ProfileUpdate(BaseModel):
    type: ProfileTypeEnum | None = None
    photo: str | None = None

class ProfileRead(ProfileBase):
    id: int
    photo: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)