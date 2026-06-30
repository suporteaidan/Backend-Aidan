from datetime import datetime, timezone
from decimal import Decimal
from app.db.base import Base
from sqlalchemy import ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ProductPrice(Base):
    """
    Represents a product price collected from a fiscal invoice.

    Each record stores the price of a product found
    in a specific market and invoice.
    """

    __tablename__ = "product_prices"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), nullable=False, index=True)

    nfe_id: Mapped[int] = mapped_column(ForeignKey("nfe.id"), nullable=False, index=True)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product = relationship("Product", back_populates="product_prices")

    market = relationship("Market", back_populates="products_price")

    nfe = relationship("NFE", back_populates="products_price")