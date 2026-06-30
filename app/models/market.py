from app.models.base import Base
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship

class Market(Base):
    """
    Represents a physical store where products are sold.

    Markets are identified through fiscal invoices and are used
    for geolocation and price comparison.
    """
    
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(primary_key=True)

    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, unique=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    address: Mapped[str] = mapped_column(String(255), nullable=False)

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

    nfes = relationship("NFE", back_populates="market")

    products_price = relationship("ProductPrice", back_populates="market")