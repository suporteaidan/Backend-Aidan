from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

from app.db.base import Base
from sqlalchemy import String, Text, Numeric, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product_price import ProductPrice


class ProductCodeType(str, Enum):
    """Supported product code types."""

    EAN = "EAN"
    INTERNAL = "INTERNAL"

class Product(Base):
    """
    Represents a unique product catalog item.

    Product information should remain stable over time.
    Price information is stored separately through ProductPrice.
    """

    __tablename__ = "products"

    __table_args__ = (
        Index(
            "uq_products_ean_product_code",
            "product_code",
            unique=True,
            postgresql_where=Text("code_type = 'EAN'"),
        ),
        Index("ix_products_ncm_code", "ncm_code"),
        Index("ix_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable= True)

    code_type: Mapped[ProductCodeType] = mapped_column(
        SQLAlchemyEnum(
            ProductCodeType,
            name="product_code_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )

    product_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    picture_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)

    ncm_code: Mapped[str | None] = mapped_column(String(8), nullable= True)

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

    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product",
        lazy="raise",
        passive_deletes=True,
    )