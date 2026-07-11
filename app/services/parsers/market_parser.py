"""
Parser responsible for extracting market information from the NFC-e HTML.

This parser is exclusively responsible for reading the HTML structure
related to the issuing establishment.

Responsibilities
----------------
- Extract market name.
- Extract CNPJ.
- Extract address information.

This parser must not:

- Normalize values.
- Call external APIs.
- Persist data.
- Apply business rules.
"""

from bs4 import BeautifulSoup

from app.schemas.nfe_data import NFEMarketData
from app.services.parsers.base_parser import BaseParser


class MarketParser(BaseParser):
    """
    Parse market information from the NFC-e HTML document.
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        super().__init__(soup)

        self._address: dict[str, str | None] | None = None

    def parse(self) -> NFEMarketData:
        """
        Extract market information from the HTML.

        Returns
        -------
        NFEMarketData
            Raw market data extracted from the HTML.
        """

        return NFEMarketData(
            market_name=self._extract_name(),
            cnpj=self._extract_cnpj(),
            market_street=self._extract_street(),
            market_number=self._extract_number(),
            market_district=self._extract_district(),
            market_city=self._extract_city(),
            market_state=self._extract_state(),
        )

    def _extract_name(self) -> str | None:
        """
        Extract the market legal name.

        Returns
        -------
        str | None
            Market legal name or None when not found.
        """

        return self._find_text(
            "div",
            class_="txtTopo",
        )

    def _extract_cnpj(self) -> str | None:
        """
        Extract the market CNPJ.

        Returns
        -------
        str | None
            Market CNPJ without formatting or None when not found.
        """

        text_elements = self._soup.find_all(
            "div",
            class_="text",
        )

        if not text_elements:
            return None

        return self._get_digits(text_elements[0])

    def _extract_address(self) -> dict[str, str | None]:
        """
        Extract and cache the complete market address.

        Returns
        -------
        dict[str, str | None]
            Parsed address components.
        """

        if self._address is not None:
            return self._address

        self._address = {
            "street": None,
            "number": None,
            "district": None,
            "city": None,
            "state": None,
        }

        text_elements = self._soup.find_all(
            "div",
            class_="text",
        )

        if len(text_elements) < 2:
            return self._address

        address = self._get_text(text_elements[1])

        if address is None:
            return self._address

        parts = [
            part.strip()
            for part in address.split(",")
            if part.strip()
        ]

        if len(parts) >= 5:
            self._address["street"] = parts[0]
            self._address["number"] = parts[1]
            self._address["district"] = parts[2]
            self._address["city"] = parts[3]
            self._address["state"] = parts[4]

        return self._address

    def _extract_street(self) -> str | None:
        """
        Extract the street name.

        Returns
        -------
        str | None
            Street name or None when not found.
        """

        return self._extract_address()["street"]

    def _extract_number(self) -> str | None:
        """
        Extract the street number.

        Returns
        -------
        str | None
            Street number or None when not found.
        """

        return self._extract_address()["number"]

    def _extract_district(self) -> str | None:
        """
        Extract the district.

        Returns
        -------
        str | None
            District or None when not found.
        """

        return self._extract_address()["district"]

    def _extract_city(self) -> str | None:
        """
        Extract the city.

        Returns
        -------
        str | None
            City or None when not found.
        """

        return self._extract_address()["city"]

    def _extract_state(self) -> str | None:
        """
        Extract the state.

        Returns
        -------
        str | None
            State or None when not found.
        """

        return self._extract_address()["state"]