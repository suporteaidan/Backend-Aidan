"""Schemas used to represent product enrichment results."""

from pydantic import BaseModel, ConfigDict


class ProductEnrichmentData(BaseModel):
    """Represent optional product data obtained from external providers."""

    model_config = ConfigDict(frozen=True)

    ncm_code: str | None = None
    brand: str | None = None
    picture_url: str | None = None