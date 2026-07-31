from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal

class NFEProductData(BaseModel):
    """
        Product extracted from a fiscal invoice.
    """
    product_code: str
    code_type: Literal["EAN", "INTERNAL"]
    name: str
    unit_price: Decimal
    total_price: Decimal
    quantity: Decimal
    ncm_code: str | None = None
    brand: str | None = None
    picture_url: str | None = None

class NFEMarketData(BaseModel):
    """
        Market data extracted from a fiscal invoice.
    """

    cnpj: str
    market_name: str
    market_street: str 
    market_number: str 
    market_district: str 
    market_city: str 
    market_state: str 

class NFEData(BaseModel):
    """
        Data extracted from a fiscal invoice.
    """

    nfe_key: str
    nfe_date: datetime
    market_data: NFEMarketData
    products_data: list[NFEProductData]

class NCMSuggestionData(BaseModel):
    """Represent an NCM suggestion returned by an external provider."""

    model_config = ConfigDict(frozen=True)

    code: str
    description: str