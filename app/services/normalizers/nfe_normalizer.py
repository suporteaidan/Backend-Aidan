"""Service responsible for normalizing extracted NFC-e data."""

import re
from decimal import Decimal, InvalidOperation

from app.schemas.nfe_data import NFEData, NFEMarketData, NFEProductData

class NfeNormalizer:
    """Normalize NFC-e data before enrichment and persistence."""

    @classmethod
    def normalize(cls, nfe_data: NFEData) -> NFEData:
        """Return a normalized copy of the extracted NFC-e data."""
        normalized_market = cls._normalize_market(nfe_data.market_data)
        normalized_products = [
            cls._normalize_product(product)
            for product in nfe_data.products_data
        ]
        return nfe_data.model_copy(
            update={
                "nfe_key": cls._normalize_digits(nfe_data.nfe_key),
                "market_data": normalized_market,
                "products_data": normalized_products,
            }
        )
    
    @classmethod
    def _normalize_market(
        cls,
        market_data: NFEMarketData,
    ) -> NFEMarketData:
        """Normalize market identification and address data."""
        return market_data.model_copy(
            update={
                "cnpj": cls._normalize_optional_digits(market_data.cnpj),
                "market_name": cls._normalize_optional_text(
                    market_data.market_name
                ),
                "market_street": cls._normalize_optional_text(
                    market_data.market_street
                ),
                "market_number": cls._normalize_optional_text(
                    market_data.market_number
                ),
                "market_district": cls._normalize_optional_text(
                    market_data.market_district
                ),
                "market_city": cls._normalize_optional_text(
                    market_data.market_city
                ),
                "market_state": cls._normalize_state(
                    market_data.market_state
                ),
            }
        )
    
    @classmethod
    def _normalize_product(
        cls,
        product_data: NFEProductData,
    ) -> NFEProductData:
        """Normalize product identification, text, and numeric data."""
        normalized_code_type = cls._normalize_code_type(
            product_data.code_type
        )

        return product_data.model_copy(
            update={
                "product_code": cls._normalize_product_code(
                    product_data.product_code,
                    normalized_code_type,
                ),
                "code_type": normalized_code_type,
                "name": cls._normalize_text(product_data.name),
                "unit_price": cls._normalize_decimal(
                    product_data.unit_price
                ),
                "total_price": cls._normalize_decimal(
                    product_data.total_price
                ),
                "quantity": cls._normalize_decimal(
                    product_data.quantity
                ),
                "ncm_code": cls._normalize_optional_digits(
                    product_data.ncm_code
                ),
                "brand": cls._normalize_optional_text(
                    product_data.brand
                ),
                "picture_url": cls._normalize_optional_text(
                    product_data.picture_url
                ),
            }
        )
    
    @staticmethod
    def _normalize_text(value: str) -> str:
        """Remove unnecessary whitespace from a required text value."""
        return " ".join(value.split())

    @classmethod
    def _normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize an optional text value."""
        if value is None:
            return None

        normalized_value = cls._normalize_text(value)
        return normalized_value or None
    
    @staticmethod
    def _normalize_digits(value: str) -> str:
        """Return only numeric characters from a required value."""
        return re.sub(r"\D", "", value)

    @classmethod
    def _normalize_optional_digits(
        cls,
        value: str | None,
    ) -> str | None:
        """Return only numeric characters from an optional value."""
        if value is None:
            return None

        normalized_value = cls._normalize_digits(value)
        return normalized_value or None
    
    @classmethod
    def _normalize_product_code(
        cls,
        value: str | None,
        code_type: str | None,
    ) -> str | None:
        """Normalize a product code according to its declared type."""
        if value is None:
            return None

        if code_type == "EAN":
            normalized_value = cls._normalize_digits(value)

        else:
            normalized_value = cls._normalize_text(value)

        return normalized_value or None
    
    @classmethod
    def _normalize_code_type(
        cls,
        value: str | None,
    ) -> str | None:
        """Normalize the supported product code type."""
        if value is None:
            return None

        normalized_value = cls._normalize_text(value).upper()

        if normalized_value not in {"EAN", "INTERNAL"}:
            raise ValueError(
                f"Unsupported product code type: {normalized_value}"
            )

        return normalized_value
    
    @staticmethod
    def _normalize_decimal(
        value: Decimal | str | int | float,
    ) -> Decimal:
        """Convert a numeric value into a normalized Decimal."""
        if isinstance(value, Decimal):
            return value

        if isinstance(value, float):
            value = str(value)

        normalized_value = str(value).strip()
        normalized_value = normalized_value.replace("R$", "").strip()
        normalized_value = normalized_value.replace(" ", "")

        if "," in normalized_value:
            normalized_value = normalized_value.replace(".", "")
            normalized_value = normalized_value.replace(",", ".")

        try:
            return Decimal(normalized_value)
        except InvalidOperation as error:
            raise ValueError(
                f"Invalid decimal value: {value}"
            ) from error
        
    @classmethod
    def _normalize_state(
        cls,
        value: str,
    ) -> str:
        """Normalize a Brazilian state abbreviation."""

        normalized_value = cls._normalize_text(value).upper()

        if len(normalized_value) != 2:
            raise ValueError(
                "Market state must be a two-letter abbreviation"
            )

        return normalized_value