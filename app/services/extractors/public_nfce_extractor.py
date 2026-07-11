"""
Extractor responsible for extracting structured data from public NFC-e HTML.

This extractor coordinates specialized parsers and builds the NFEData schema.

Responsibilities
----------------
- Parse the public NFC-e HTML document.
- Extract the NFC-e access key.
- Extract the NFC-e issue date.
- Delegate market extraction to MarketParser.
- Delegate product extraction to ProductParser in the future.
- Return an NFEData object.

This extractor must not:

- Persist data.
- Call external APIs.
- Enrich products.
- Apply database rules.
"""

from app.services.extractors.base_extractor import BaseNFEExtractor
from app.services.parsers.market_parser import MarketParser
from app.schemas.nfe_data import NFEData
from app.services.parsers.product_parser import ProductParser

from bs4 import BeautifulSoup
from datetime import datetime
import re

class PublicNFCeExtractor(BaseNFEExtractor):
    """
    Extract structured data from a public NFC-e HTML page.
    """

    def extract(self, html: str) -> NFEData:
        """
        Extract NFC-e data from HTML.

        Parameters
        ----------
        html : str
            Public NFC-e HTML content.

        Returns
        -------
        NFEData
            Structured NFC-e data.
        """

        soup = BeautifulSoup(html, "lxml")

        return NFEData(
            nfe_key=self._extract_nfe_key(soup),
            nfe_date=self._extract_nfe_date(soup),
            market_data=MarketParser(soup).parse(),
            products_data=ProductParser(soup).parse(),
        )
    
    def _extract_nfe_key(self, soup: BeautifulSoup) -> str:
        """
        Extract the NFC-e access key.

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML document.

        Returns
        -------
        str
            NFC-e access key without formatting.

        Raises
        ------
        ValueError
            If the NFC-e access key is not found.
        """

        element = soup.find("span", class_="chave")

        if not element:
            raise ValueError("NFC-e access key not found")

        key = "".join(filter(str.isdigit, element.get_text()))

        if not key:
            raise ValueError("NFC-e access key is empty")
        return key

    def _extract_nfe_date(self, soup: BeautifulSoup) -> datetime:
        """
        Extract the NFC-e issue date.

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML document.

        Returns
        -------
        datetime
            NFC-e issue date.

        Raises
        ------
        ValueError
            If the NFC-e issue date is not found.
        """

        infos_element = soup.find(
            "div",
            id="infos",
        )

        if infos_element is None:
            raise ValueError("NFC-e information block not found.")
        
        text = infos_element.get_text(
            separator=" ",
            strip=True,
        )

        match = re.search(r"Emissão:\s*(\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2}:\d{2})", text)

        if match is None:
            raise ValueError("NFC-e issue date not found.")
        
        date_text = match.group(1)

        return datetime.strptime(date_text, "%d/%m/%Y %H:%M:%S")