from decimal import Decimal
from pydantic import BaseModel
from datetime import datetime

class NFEProductData(BaseModel):
    """
        Product extracted from a fiscal invoice.
    """
    product_code: str
    code_type: str
    name: str
    unit_price: Decimal
    total_price: Decimal
    quantity: Decimal

class NFEMarketData(BaseModel):
    """
        Market data extracted from a fiscal invoice.
    """

    cnpj: str
    market_name: str
    market_address: str

class NFEData(BaseModel):
    """
        Data extracted from a fiscal invoice.
    """

    nfe_key: str
    nfe_date: datetime
    market_data: NFEMarketData
    products_data: list[NFEProductData]