"""Alert rule model — PRD §14.3, Phase 2."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # rule_type values: "consecutive_failures" | "http_error" | "timeout" | "zero_data" | "token_expiry"
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "sync_job" | "data_source"
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    threshold: Mapped[int] = mapped_column(Integer, default=1)
    window_minutes: Mapped[int] = mapped_column(Integer, default=15)
    channels: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
