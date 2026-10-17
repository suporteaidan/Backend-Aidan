from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product_price import ProductPrice
    from app.models.market import Market
    from app.models.user import User



class NFE(Base):
    """
    Represents a fiscal invoice imported from a QR Code.

    An invoice belongs to a user and a market.
    """

    __tablename__ = "nfe"

    __table_args__ = (
        Index("ix_nfes_market_nfe_date", "market_id", "nfe_date"),
        Index(
            "ix_nfes_user_nfe_date",
            "user_id",
            "nfe_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
            ForeignKey(
                "users.id",
                onupdate="CASCADE",
                ondelete="SET NULL"
            ),
            nullable=True,
            index=True,
        )

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id", ondelete="CASCADE"), nullable=False)

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

    user = relationship("User", back_populates="nfes")

    market: Mapped["Market"] = relationship(
        back_populates="nfe",
        lazy="raise",
    )
    product_prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="nfe",
        lazy="raise",
        passive_deletes=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="nfes",
        lazy="raise",
    )