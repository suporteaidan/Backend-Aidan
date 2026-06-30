from abc import ABC, abstractmethod
from app.schemas.nfe_data import NFEData

class BaseNFEExtractor(ABC):
    """
    Base contract for NFC-e extractors.

    All extractors must return a standardized NFEData object.
    """

    @abstractmethod
    async def extract(
        self,
        qr_code_url: str,
    ) -> NFEData:
        """
        Extract invoice information from a QR Code URL.

        Args:
            qr_code_url: NFC-e QR Code URL.

        Returns:
            Standardized invoice data.
        """
        raise NotImplementedError