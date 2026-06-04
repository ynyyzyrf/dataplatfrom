"""Dashboard and widget models — PRD §10, §16.5, §16.6."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DashboardStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), default="private", nullable=False)
    status: Mapped[str] = mapped_column(Enum(DashboardStatus), default=DashboardStatus.DRAFT, nullable=False)

    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    widgets: Mapped[list["DashboardWidget"]] = relationship(back_populates="dashboard", cascade="all, delete-orphan")
    shares: Mapped[list["DashboardShare"]] = relationship(back_populates="dashboard", cascade="all, delete-orphan")


class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id: Mapped[str] = mapped_column(String(36), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    component_source: Mapped[str] = mapped_column(String(20), default="system", nullable=False)
    component_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    component_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    widget_type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    query_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    props_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_binding_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    event_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    visual_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    position_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    dashboard: Mapped["Dashboard"] = relationship(back_populates="widgets")
