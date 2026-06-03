"""SQLAlchemy ORM base model with common columns and helpers."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.database import Base


class TimestampMixin:
    """Mixin that adds ``created_at`` and ``updated_at`` to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseTimestamp(Base, TimestampMixin):
    """Declarative base with timestamp columns."""

    __abstract__ = True
