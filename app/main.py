"""Application entry point.

This module initializes the FastAPI application, configures global
application resources, and registers the versioned API router.

Feature-specific routes are composed outside this module so that the
application entry point remains independent from individual API domains.
"""

from fastapi import FastAPI

from app.api.v1.router import api_router


app = FastAPI(
    title="Aidan API",
    description="API for Aidan application",
    version="1.0.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return the current API health status."""

    return {"status": "ok"}


app.include_router(
    api_router,
    prefix="/api/v1",
)