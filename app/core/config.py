"""
Application configuration module.

This module is responsible for loading environment variables and exposing
application settings in a centralized and typed way.
"""

from dotenv import load_dotenv
from functools import lru_cache
from pydantic import BaseModel
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """
    Application settings.

    This class defines all environment variables used by the application.
    """

    # Application settings
    APP_NAME: str = "Aidan API"
    envitoment: str = os.getenv("ENVIRONMENT", "development")

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/aidan")

    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

@lru_cache
def get_settings() -> Settings:
    """
    Get application settings.

    This function returns a cached instance of the Settings class,
    ensuring that environment variables are loaded only once.
    """
    return Settings()