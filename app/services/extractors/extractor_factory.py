"""
Factory responsible for creating extractor instances.

At the current MVP stage, the application supports a single extractor
responsible for parsing HTML returned by the Brazilian public NFC-e
consultation page.

The factory was introduced to keep the pipeline decoupled from concrete
implementations and to simplify future support for additional data sources
or document formats.

Future examples:

- Public NFC-e HTML
- Authorized XML
- OCR from printed receipts
- Third-party provider APIs
"""

from app.services.extractors.base_extractor import BaseNFEExtractor
from app.services.extractors.public_nfce_extractor import PublicNFCeExtractor

class ExtractorFactory:
    """
    Factory responsible for creating extractor instances.

    During the MVP, only the public NFC-e HTML extractor is available.
    """

    def create(self) -> BaseNFEExtractor:
        """
        Create an extractor instance.

        Returns
        -------
        BaseNFEExtractor
            Concrete extractor implementation.
        """

        return PublicNFCeExtractor()

