from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class NFE(Base):
    """
    Represents a fiscal invoice imported from a QR Code.

    An invoice belongs to a user and a market.
    """

    __tablename__ = "nfe"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False)

    nfe_key: Mapped[str] = mapped_column(String(44), nullable=False, index=True, unique=True)

    nfe_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="nfe")

    market = relationship("Market", back_populates="nfe")

    products_price = relationship("ProductPrice", back_populates="nfe")