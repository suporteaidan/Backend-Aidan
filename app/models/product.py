from app.models.base import Base
from sqlalchemy import String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

class Product(Base):
    """
    Represents a unique product catalog item.

    Product information should remain stable over time.
    Price information is stored separately through ProductPrice.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    product_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True, unique=True)

    code_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    picture: Mapped[str | None] = mapped_column(String(255), nullable=True)

    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)

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

    product_prices = relationship("ProductPrice", back_populates="product")