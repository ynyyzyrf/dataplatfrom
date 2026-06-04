"""Dashboard sharing model — PRD §13.2, Phase 2."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DashboardShare(Base):
    __tablename__ = "dashboard_shares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id: Mapped[str] = mapped_column(String(36), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    shared_with_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shared_with_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    permission_level: Mapped[str] = mapped_column(String(20), default="view", nullable=False)  # "view" | "edit"

    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    dashboard: Mapped["Dashboard"] = relationship(back_populates="shares")
