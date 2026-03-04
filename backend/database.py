"""
Async SQLAlchemy database setup for AutoPost2.
Uses SQLite via aiosqlite for local dev. Swap connection string for PostgreSQL later.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# SQLite database file lives next to this module
DB_PATH = os.path.join(os.path.dirname(__file__), "autopost.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables. Called once on app startup."""
    from db_models import Post, Analytics  # noqa: F401 — ensure models are registered
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async session."""
    async with async_session() as session:
        yield session
