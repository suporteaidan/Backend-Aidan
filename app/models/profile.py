"""
Profile model definition.

This module defines the Profile table using SQLAlchemy 2.0 ORM syntax.
The Profile represents the user's subscription type and related metadata.

Why SQLAlchemy 2.x?
- Strong typing with `Mapped`
- Better IDE support and autocomplete
- Future-proof and recommended by SQLAlchemy
- Cleaner integration with Alembic and FastAPI
"""

from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING


from sqlalchemy import String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User

class ProfileTypeEnum(str , Enum):
    """
    Enum that represents the possible profile types.
    """
    FREE = "free"
    PREMIUM = "premium"

class Profile(Base):
    """
    Profile database model.

    This table stores information related to the user's profile,
    such as subscription type and profile photo.
    """

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(20), default=ProfileTypeEnum.FREE.value, nullable=False)
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship 
    user: Mapped["User"] = relationship("User", back_populates="profile", uselist=False)
