"""
Application entry point.

This module initializes the FastAPI application, configures global
middleware, and includes API routes.
"""

from fastapi import FastAPI

from app.api.v1.users import router as user_router

from app.api.v1.users import router as user_router

app = FastAPI(
    title = "Aindan API",
    description = "API for Aindan application",
    version = "1.0.0",
)

# healthcheck endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# api v1
app.include_router(user_router, prefix="/api/v1")