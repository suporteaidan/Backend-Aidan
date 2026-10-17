from datetime import datetime, timezone
from decimal import Decimal
from app.db.base import Base
from app.models.nfe import NFE
from sqlalchemy import ForeignKey, Numeric, DateTime, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.market import Market
    from app.models.product import Product



class ProductPrice(Base):
    """
    Represents a product price collected from a fiscal invoice.

    Each record stores the price of a product found
    in a specific market and invoice.
    """

    __tablename__ = "product_prices"

    __table_args__ = (
        CheckConstraint(
            "unit_price >= 0",
            name="ck_product_prices_unit_price_non_negative",
        ),
        CheckConstraint(
            "total_price >= 0",
            name="ck_product_prices_total_price_non_negative",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_product_prices_quantity_positive",
        ),
        Index(
            "ix_product_prices_product_collected_at",
            "product_id",
            "collected_at",
        ),
        Index(
            "ix_product_prices_market_product_collected_at",
            "market_id",
            "product_id",
            "collected_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey(
            "markets.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    nfe_id: Mapped[int] = mapped_column(
        ForeignKey(
            "nfe.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)

    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    product: Mapped["Product"] = relationship(
        back_populates="prices",
        lazy="raise",
    )
    market: Mapped["Market"] = relationship(
        back_populates="product_prices",
        lazy="raise",
    )
    nfe: Mapped["NFE"] = relationship(
        back_populates="product_prices",
        lazy="raise",
    )