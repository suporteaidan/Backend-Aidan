"""
Parser responsible for extracting product information from the NFC-e HTML.

This parser is exclusively responsible for reading the HTML structure
related to invoice products.

Responsibilities
----------------
- Find the products table.
- Extract product rows.
- Convert each product row into NFEProductData.

This parser must not:

- Normalize product names.
- Enrich products with external APIs.
- Persist data.
- Apply database rules.
"""

from decimal import Decimal, InvalidOperation

from app.services.parsers.base_parser import BaseParser
from app.schemas.nfe_data import NFEProductData

from bs4 import BeautifulSoup, Tag

class ProductParser(BaseParser):
    """
    Parse product information from the NFC-e HTML document.
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        super().__init__(soup)

    def parse(self) -> list[NFEProductData]:
        """
        Extract all products from the NFC-e HTML.

        Returns
        -------
        list[NFEProductData]
            Raw product data extracted from the HTML.
        """

        rows = self._extract_product_rows()

        products =  [ 
            self._parse_product_row(row)
            for row in rows
        ]

        return products

    def _extract_product_rows(self) -> list[Tag]:
        """
        Extract all product rows from the products table.

        Returns
        -------
        list[Tag]
            HTML table rows representing products.
        """

        table = self._find(
            "table",
            id="tabResult",
        )

        if table is None:
            raise ValueError("Products table not found.")

        rows = table.find_all("tr")

        return [
            row
            for row in rows
            if isinstance(row, Tag)
        ]
    
    def _parse_product_row(self, row: Tag) -> NFEProductData:
        """
        Convert a product row into NFEProductData.

        Parameters
        ----------
        row : Tag
            HTML table row representing a product.

        Returns
        -------
        NFEProductData
            Raw product data extracted from the row.
        """

        return NFEProductData(
            product_code=self._extract_product_code(row),
            code_type=self._extract_code_type(row),
            name=self._extract_name(row),
            unit_price=self._extract_unit_price(row),
            total_price=self._extract_total_price(row),
            quantity=self._extract_quantity(row),
        )
    
    def _extract_product_code(self, row: Tag) -> str:
        """
        Extract the product code from a product row.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        str
            Product code.

        Raises
        ------
        ValueError
            If the product code is not found.
        """

        element = row.find(
            "span",
            class_="RCod",
        )

        code = self._get_digits(element)

        if code is None:
            raise ValueError("Product code not found.")

        return code


    def _extract_code_type(self, row: Tag) -> str:
        """
        Determine the product code type.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        str
            Product code type.
        """

        product_code = self._extract_product_code(row)

        if len(product_code) == 13:
            return "EAN"

        return "INTERNAL"


    def _extract_name(self, row: Tag) -> str:
        """
        Extract the product name from a product row.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        str
            Product name.

        Raises
        ------
        ValueError
            If the product name is not found.
        """

        element = row.find(
            "span",
            class_="txtTit",
        )

        name = self._get_text(element)

        if name is None:
            raise ValueError("Product name not found.")

        return name


    def _extract_unit_price(self, row: Tag):
        """
        Extract the product unit price.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        Decimal
            Product unit price.

        Raises
        ------
        ValueError
            If the unit price is not found or is invalid.
        """

        element = row.find(
            "span",
            class_="RvlUnit",
        )

        text = self._get_text(element)

        if text is None:
            raise ValueError("Product unit price not found.")

        value = text.replace("Vl. Unit.:", "").strip()

        return self._convert_to_decimal(
            value=value,
            field_name="Product unit price",
        )


    def _extract_total_price(self, row: Tag):
        """
        Extract the product total price.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        Decimal
            Product total price.

        Raises
        ------
        ValueError
            If the total price is not found or is invalid.
        """

        element = row.find(
            "span",
            class_="valor",
        )

        text = self._get_text(element)

        if text is None:
            raise ValueError("Product total price not found.")

        return self._convert_to_decimal(
            value=text,
            field_name="Product total price",
        )


    def _extract_quantity(self, row: Tag):
        """
        Extract the product quantity.

        Parameters
        ----------
        row : Tag
            HTML table row representing a single product.

        Returns
        -------
        Decimal
            Product quantity.

        Raises
        ------
        ValueError
            If the quantity is not found or is invalid.
        """

        element = row.find(
            "span",
            class_="Rqtd",
        )

        text = self._get_text(element)

        if text is None:
            raise ValueError("Product quantity not found.")

        value = text.replace("Qtde.:", "").strip()

        return self._convert_to_decimal(
            value=value,
            field_name="Product quantity",
        )
    
    @staticmethod
    def _convert_to_decimal(
        value: str,
        field_name: str,
    ) -> Decimal:
        """
        Convert a Brazilian numeric string into Decimal.

        Parameters
        ----------
        value : str
            Numeric string using Brazilian decimal formatting.
        field_name : str
            Field name used in the error message.

        Returns
        -------
        Decimal
            Converted decimal value.

        Raises
        ------
        ValueError
            If the value cannot be converted.
        """

        normalized_value = value.replace(".", "").replace(",", ".")

        try:
            return Decimal(normalized_value)

        except InvalidOperation as error:
            raise ValueError(
                f"{field_name} has an invalid value: {value}."
            ) from error