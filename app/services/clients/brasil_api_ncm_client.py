"""Client implementation for searching NCM data through BrasilAPI."""

from typing import Any

from app.exceptions.external_provider import ExternalProviderResponseError, ExternalProviderError
import httpx

from app.schemas.nfe_data import NCMSuggestionData
from app.services.clients.base_ncm_client import BaseNCMClient

class BrasilApiNcmClient(BaseNCMClient):
    """Search for NCM suggestions using the BrasilAPI NCM service."""

    Base_URL = "https://brasilapi.com.br/api/ncm/v1/"

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialize the client with an asynchronous HTTP client."""
        self.client = client

    async def search_by_description(self, description: str) -> list[NCMSuggestionData]:
        """Search for NCM suggestions matching a product description."""

        try:
            response = await self.client.get(
                self.Base_URL,
                params = {"search": description}
            )

            response.raise_for_status()
            
        except httpx.HTTPError as e:
            raise ExternalProviderError("Failed to retrieve NCM suggestions from BrasilAPI.") from e

        try:
            data = response.json()

        except ValueError as e:
            raise ExternalProviderResponseError("Invalid JSON response from BrasilAPI.") from e
        
        if not isinstance(data, list):
            raise ExternalProviderResponseError(
                "BrasilAPI returned an unexpected response format."
            )
        
        suggestions = []

        for item in data:
            if not isinstance(item, dict):
                raise ExternalProviderResponseError(
                    "BrasilAPI returned an invalid NCM item."
                )

            suggestions.append(self._build_suggestion(item))

        return suggestions
    
    @staticmethod
    def _build_suggestion(data: dict[str, Any]) -> NCMSuggestionData:
        """Convert a BrasilAPI NCM response item into an internal schema."""

        code = data.get("codigo")
        description = data.get("descricao")

        if not isinstance(code, str) or not code.strip():
            raise ExternalProviderResponseError(
                "BrasilAPI returned an NCM item with an invalid or missing 'codigo'."
            )

        if not isinstance(description, str) or not description.strip():
            raise ExternalProviderResponseError(
                "BrasilAPI returned an NCM item with an invalid or missing 'descricao'."
            )

        return NCMSuggestionData(
            code = code,
            description = description
        )
    

