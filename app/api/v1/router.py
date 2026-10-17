"""API version 1 router configuration.

This module centralizes the registration of all route groups that belong to
version 1 of the Aidan API.

Each application domain defines its own APIRouter inside the routes package.
Those routers are collected here and exposed through a single API router.

Centralizing route registration prevents the application entry point from
depending directly on every feature module and makes it easier to add new
domains as the application grows.

The ``/api/v1`` prefix is applied when this router is registered in the main
FastAPI application.
"""

from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.nfe import router as nfe_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(nfe_router)