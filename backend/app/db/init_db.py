from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """
    Initialize database tables.

    This function will create tables based on imported SQLAlchemy models.
    In production, Alembic migrations will be the official way to evolve schema.
    """

    Base.metadata.create_all(bind=engine)