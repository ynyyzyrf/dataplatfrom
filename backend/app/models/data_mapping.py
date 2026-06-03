"""Field mapping model — PRD §8.4, §16.4."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FieldMapping(Base):
    __tablename__ = "data_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False)
    target_table_name: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_key_config: Mapped[dict] = mapped_column(JSON, default=dict)
    field_mappings: Mapped[dict] = mapped_column(JSON, default=dict)
    table_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    data_source: Mapped["DataSource"] = relationship(back_populates="mappings")

    def __repr__(self) -> str:
        return f"<FieldMapping {self.target_table_name}>"
