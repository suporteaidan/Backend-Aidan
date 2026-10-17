"""Schemas for NFC-e import requests and responses.

This module defines the data contracts used by the HTTP layer when a client
requests the import of an NFC-e through its public QR Code URL.

The request schema intentionally contains only the QR Code URL. The user
identifier must not be accepted from the client because it will be obtained
from the authenticated application context.

Keeping the HTTP schema separated from the internal NFEData schema prevents
transport-layer concerns from being mixed with extracted fiscal document
data.

The schemas defined here are designed to be consumed by FastAPI endpoints
and validated automatically by Pydantic before the NFC-e processing pipeline
is executed.
"""

from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict


class NFEImportRequest(BaseModel):
    """Represent the data required to import an NFC-e."""

    qr_code_url: HttpUrl

class NFEImportResponse(BaseModel):
    """Represent the result of a successfully imported NFC-e."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nfe_key: str
    nfe_date: datetime
    market_id: int
    user_id: int | None