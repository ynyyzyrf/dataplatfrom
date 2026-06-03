"""SQLAlchemy engine, session, and base utilities.

Provides:
- ``async_engine`` — async DB engine
- ``async_session_factory`` — callable to create ``AsyncSession``
- ``get_async_db`` — FastAPI dependency that yields a session
- ``Base`` — declarative base for all ORM models
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

__all__ = [
    "Base",
    "async_engine",
    "async_session_factory",
    "get_async_db",
    "AsyncSession",
]


# Engine & session factory

async_engine = create_async_engine(
    settings.database_url_plain,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base model

class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""
    pass


# FastAPI dependency

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session and roll back on exit."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
