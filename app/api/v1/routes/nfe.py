"""HTTP routes for NFC-e import operations.

This module exposes the API endpoint responsible for starting the complete
NFC-e import pipeline from a public QR Code URL.

The route receives only transport-layer data through NFEImportRequest.
Fiscal document extraction, normalization, enrichment, and persistence are
delegated entirely to NfePipeline.

The authenticated user is obtained from the FastAPI authentication
dependency instead of being accepted in the request body. This prevents a
client from assigning an NFC-e import to another user by manually providing
a user identifier.

The endpoint follows the application's separation of responsibilities:

HTTP request
    ↓
NFEImportRequest
    ↓
Authenticated User
    ↓
NfePipeline
    ↓
Persisted NFE
    ↓
NFEImportResponse

The route contains no database queries, repository construction, external
HTTP integration, fiscal document parsing, or transaction management.
Those responsibilities belong to their respective application layers.
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.nfe import get_nfe_pipeline
from app.models.user import User
from app.schemas.nfe_import import (
    NFEImportRequest,
    NFEImportResponse,
)
from app.services.nfe_pipeline import NfePipeline

router = APIRouter(
    prefix="/nfes",
    tags=["NFC-e"],
)

@router.post(
    "/import",
    response_model=NFEImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_nfe(
    request: NFEImportRequest,
    current_user: User = Depends(get_current_user),
    pipeline: NfePipeline = Depends(get_nfe_pipeline),
) -> NFEImportResponse:
    """Import and persist an NFC-e from its public QR Code URL."""

    nfe = await pipeline.process(
        qr_code_url=str(request.qr_code_url),
        user_id=current_user.id,
    )

    return NFEImportResponse.model_validate(nfe)