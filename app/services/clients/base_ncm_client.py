"""Abstract contract for NCM search clients."""

from abc import ABC, abstractmethod

from app.schemas.nfe_data import NCMSuggestionData


class BaseNCMClient(ABC):
    """Define the contract for external NCM search providers."""

    @abstractmethod
    async def search_by_description(
        self,
        description: str,
    ) -> list[NCMSuggestionData]:
        """Search for NCM suggestions using a product description."""