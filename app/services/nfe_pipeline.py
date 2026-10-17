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
from app.services.extractors.extractor_factory import ExtractorFactory
from app.services.normalizers.nfe_normalizer import NfeNormalizer
from app.services.enrichment.nfe_enrichment_service import NFEEnrichmentService
from app.services.persistence.nfe_persistence_service import NFEPersistenceService

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
    - Persistence service 

    This class intentionally contains no business logic.
    """

    def __init__(
        self,
        client: NFEClient,
        extractor_factory: ExtractorFactory,
        normalizer: NfeNormalizer,
        enrichment_service: NFEEnrichmentService,
        persistence_service: NFEPersistenceService
    ) -> None:
        self._client = client
        self._extractor_factory = extractor_factory
        self._normalizer = normalizer
        self._enrichment_service = enrichment_service
        self._pesistence_service = persistence_service

    async def process(self, qr_code_url: str, user_id: int) -> NFEData:
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
        html = await self._client.fetch_nfe_html(qr_code_url)

        # Get the appropriate extractor implementation.
        extractor = self._extractor_factory.create()

        # Parse the HTML into a structured data object.
        extracted_data = extractor.extract(html)

        # Normalize values such as dates, decimals and documents.
        normalized_nfe_data = self._normalizer.normalize(extracted_data)

        # Enrich the normalized data using external services.
        enriched_nfe_data = await self._enrichment_service.enrich(
            normalized_nfe_data
        )


        return await self._pesistence_service.persist(
            nfe_data= enriched_nfe_data,
            user_id= user_id,
        )