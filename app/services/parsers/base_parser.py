"""
Base parser containing helper methods shared by all HTML parsers.

This class centralizes common operations performed while navigating the
BeautifulSoup document, reducing duplicated code across specialized parsers.

Responsibilities
----------------
- Find HTML elements safely.
- Extract cleaned text.
- Return None when an element does not exist.

This class must not contain business rules or normalization logic.
"""

from bs4 import BeautifulSoup, Tag


class BaseParser:
    """
    Base class for all HTML parsers.
    """

    def __init__(self, soup: BeautifulSoup) -> None:
        self._soup = soup

    def _find(self, name: str, **kwargs) -> Tag | None:
        """
        Find the first HTML element matching the given parameters.

        Parameters
        ----------
        name : str
            HTML tag name.

        Returns
        -------
        Tag | None
            The first matching HTML element, or None if not found.
        """

        return self._soup.find(name, **kwargs)

    def _find_text(self, name: str, **kwargs) -> str | None:
        """
        Find an HTML element and return its cleaned text.

        Parameters
        ----------
        name : str
            HTML tag name.

        Returns
        -------
        str | None
            Cleaned text or None if the element is not found.
        """

        element = self._find(name, **kwargs)

        return self._get_text(element)

    @staticmethod
    def _get_text(element: Tag | None) -> str | None:
        """
        Extract and clean the text from an HTML element.

        Parameters
        ----------
        element : Tag | None
            The HTML element to extract text from.

        Returns
        -------
        str | None
            The cleaned text, or None if the element is None.
        """

        if element is None:
            return None

        text = element.get_text(separator=" ", strip=True)

        return text or None

    def _get_digits(self, element: Tag | None) -> str | None:
        """
        Extract only digits from an HTML element text.

        Parameters
        ----------
        element : Tag | None
            The HTML element to extract digits from.

        Returns
        -------
        str | None
            Digits-only text or None if the element does not exist.
        """

        text = self._get_text(element)

        if text is None:
            return None

        digits = "".join(filter(str.isdigit, text))

        return digits or None