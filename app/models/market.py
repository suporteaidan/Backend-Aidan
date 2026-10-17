from app.db.base import Base
from sqlalchemy import String, Float, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.nfe import NFE
    from app.models.product_price import ProductPrice


class Market(Base):
    """
    Represents a physical store where products are sold.

    Markets are identified through fiscal invoices and are used
    for geolocation and price comparison.
    """
    
    __tablename__ = "markets"

    __table_args__ = (
        Index("ix_markets_market_name", "market_name"),
        Index(
            "ix_markets_location",
            "market_state",
            "market_city",
            "market_district",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, unique=True, index=True)

    market_name: Mapped[str] = mapped_column(String(255), nullable=False)

    market_street: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    market_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    market_district: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    market_city: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    market_state: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

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

    nfe: Mapped[list["NFE"]] = relationship(
        back_populates="market",
        lazy="raise",
        passive_deletes=True,
    )

    product_prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="market",
        lazy="raise",
        passive_deletes=True,
    )