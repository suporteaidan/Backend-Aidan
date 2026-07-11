"""
Main pipeline responsible for orchestrating the NFC-e processing flow.

The pipeline coordinates every stage required to transform a QR Code URL
into persisted data.

Pipeline flow:

QR Code URL
    ↓
NFEClient
    ↓
HTML
    ↓
Extractor
    ↓
NFEData
    ↓
Normalizer
    ↓
Enrichment
    ↓
Persistence

The pipeline does not contain business rules.
Its only responsibility is coordinating the execution order of each
specialized service.
"""

from app.schemas.nfe_data import NFEData
from app.services.clients.nfe_client import NFEClient
from app.services.extractors.base_extractor import BaseExtractor



class NfePipeline:
    """
    Coordinates the complete NFC-e processing workflow.

    Responsibilities
    ----------------
    - Download HTML from the public NFC-e page.
    - Select the correct extractor.
    - Extract raw structured data.
    - Normalize extracted values.
    - Enrich business information.
    - Persist the final data.

    This class intentionally contains no business logic.
    """

    def __init__(
        self,
        client: NFEClient,
        extractor_factory: ExtractorFactory,
        normalizer: NFENormalizer,
        enrichment_service: NFEEnrichmentService,
        persistence_service: NFEPersistenceService,
    ) -> None:
        self._client = client
        self._extractor_factory = extractor_factory
        self._normalizer = normalizer
        self._enrichment_service = enrichment_service
        self._persistence_service = persistence_service

    async def process(self, qr_code_url: str) -> NFEData:
        """
        Execute the complete NFC-e processing pipeline.

        Parameters
        ----------
        qr_code_url : str
            Public NFC-e QR Code URL.

        Returns
        -------
        NFEData
            Enriched invoice data after processing and persistence.
        """

        # Download the HTML from the public NFC-e page.
        html = await self._client.fetch(qr_code_url)

        # Get the appropriate extractor implementation.
        extractor: BaseExtractor = self._extractor_factory.create()

        # Parse the HTML into a structured data object.
        raw_nfe_data = extractor.extract(html)

        # Normalize values such as dates, decimals and documents.
        normalized_nfe_data = self._normalizer.normalize(raw_nfe_data)

        # Enrich the normalized data using external services.
        enriched_nfe_data = await self._enrichment_service.enrich(
            normalized_nfe_data
        )

        # Persist the enriched data into the database.
        await self._persistence_service.save(enriched_nfe_data)

        return enriched_nfe_data