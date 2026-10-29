
import pytest
import pytest_asyncio 
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from collections.abc import AsyncIterator
from httpx import ASGITransport, AsyncClient

from app.db.base import Base

from app.models.market import Market
from app.models.nfe import NFE
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.profile import Profile
from app.models.user import User
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Provide an asynchronous client for the FastAPI app."""

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

@pytest_asyncio.fixture
async def db_session():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            yield session
    finally:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        finally:
            await engine.dispose()

@event.listens_for(engine.sync_engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record,
) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
