"""
User model definition.

This module defines the User table using SQLAlchemy 2.x ORM.
The User represents the main entity of the system and is linked
to a Profile through a one-to-one relationship.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional



from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile

class User(Base):
    """
    User database model.

    This table stores authentication and personal information
    about users and maintains a one-to-one relationship with Profile.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="RESTRICT"), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    cpf: Mapped[Optional[str]] = mapped_column(String(14), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)