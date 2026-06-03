"""Data source model — PRD §6, §16.1."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuthType(str, enum.Enum):
    NONE = "none"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"


class DataSourceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class RequestMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    group: Mapped[str | None] = mapped_column(String(100), nullable=True)

    request_method: Mapped[str] = mapped_column(String(10), nullable=False)
    request_url: Mapped[str] = mapped_column(Text, nullable=False)
    auth_type: Mapped[str] = mapped_column(String(20), nullable=False)
    auth_config_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    headers_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    query_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    body_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[str] = mapped_column(String(20), default=DataSourceStatus.ACTIVE, nullable=False)

    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    sync_jobs: Mapped[list["SyncJob"]] = relationship(back_populates="data_source")
    mappings: Mapped[list["FieldMapping"]] = relationship(back_populates="data_source")

    def __repr__(self) -> str:
        return f"<DataSource {self.name}>"
