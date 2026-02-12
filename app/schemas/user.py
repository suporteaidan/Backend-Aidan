from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

from app.schemas.profile import ProfileRead

class UserBase(BaseModel):
    name: str
    cpf: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    address: str | None = None
    phone: str | None = None

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    phone: str | None = None

class UserRead(UserBase):
    id: Optional[int] = None
    profile: ProfileRead | None = None
    address: str | None = None
    email: EmailStr
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str