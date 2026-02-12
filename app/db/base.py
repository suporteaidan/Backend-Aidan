from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base declarative class for all ORM models.

    All SQLAlchemy models in the application must inherit from this class.
    This allows Alembic to detect metadata for migrations.
    """
