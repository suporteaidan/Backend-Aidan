from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field

class ProductBase(BaseModel):
    """
    Base schema for product data.
    """

    name: str = Field(min_length=1, max_length=255)

    price: Decimal = Field(gt=0)

    description: str | None = Field(default=None, max_length=500)

    barcode: str = Field(min_length=1, max_length=50)

    picture: str | None = Field(default=None, max_length=255)

    weight: Decimal | None = Field(default=None, gt=0)

