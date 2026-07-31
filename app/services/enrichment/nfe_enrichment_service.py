"""Service responsible for enriching normalized NFC-e data."""

import logging
import re

from app.services.clients.base_ncm_client import BaseNCMClient
from app.schemas.nfe_data import NFEData,NFEProductData
from app.exceptions.external_provider import ExternalProviderError


logger = logging.getLogger(__name__)

class NFEEnrichmentService:
    """Enrich NFC-e products with data obtained from external providers."""

    def __init__(self, ncm_client: BaseNCMClient) -> None:
        """Initialize the service with an NCM search client."""
        self._ncm_client = ncm_client

    async def enrich(self, nfe_data: NFEData) -> NFEData:
        """Return a new NFC-e representation with enriched product data."""

        enriched_products = []

        for product in nfe_data.products_data:
            enriched_product = await self._enrich_product(product)
            enriched_products.append(enriched_product)

        # model_copy came from pydantic
        return nfe_data.model_copy(
            update={"products_data": enriched_products}
        )
    
    async def _enrich_product(
            self,
            product: NFEProductData,
    ) -> NFEProductData:
        """Enrich an internal product with the first valid NCM suggestion."""

        if product.code_type != "INTERNAL":
            return product
        
        if product.ncm_code:
            return product
        
        try:
            suggestion = await self._ncm_client.search_by_description(
                product.name
            )
        except ExternalProviderError:
            logger.warning(
                "NCM enrichment failed for product '%s'.",
                product.name,
                exc_info=True,
            )

            return product
        
        if not suggestion:
            return product
        
        ncm_code = self._normalize_ncm_code(suggestion[0].code)

        if ncm_code is None:
            logger.warning(
                "The NCM provider returned an invalid code for product '%s'.",
                product.name,
            )
            return product
        
        return product.model_copy(
            update={"ncm_code": ncm_code}
        )
    
    @staticmethod
    def _normalize_ncm_code(code: str) -> str | None:
        """Return an eight-digit NCM code or None when the value is invalid."""
        normalized_code = re.sub(r"\D", "", code)

        if len(normalized_code) != 8:
            return None

        return normalized_code