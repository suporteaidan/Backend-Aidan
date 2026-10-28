"""
Alembic environment configuration.

This file configures Alembic to run migrations using SQLAlchemy 2.x.
Even if the application uses async engines, Alembic itself runs
synchronously.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base

from app.models.profile import Profile
from app.models.user import User
from app.models.market import Market
from app.models.nfe import NFE
from app.models.product import Product, ProductCodeType
from app.models.product_price import ProductPrice



# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load settings
settings = get_settings()

sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg2://",
    1,
)

config.set_main_option(
    "sqlalchemy.url",
    sync_database_url.replace("%", "%%"),
)

# Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """
    context.configure(
        url=sync_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=(
            {"sslmode": "require"}
            if settings.database_ssl
            else {}
        ),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
