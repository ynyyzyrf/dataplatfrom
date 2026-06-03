"""Sync job & run models — PRD §7, §14, §16.2, §16.3."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScheduleType(str, enum.Enum):
    INTERVAL = "interval"
    CRON = "cron"


class SyncMode(str, enum.Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    PAGED = "paged"


class WriteMode(str, enum.Enum):
    INSERT = "insert"
    UPSERT = "upsert"
    REPLACE = "replace"
    APPEND = "append"


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source_id: Mapped[str] = mapped_column(String(36), ForeignKey("data_sources.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    schedule_type: Mapped[str] = mapped_column(String(20), nullable=False)
    schedule_config: Mapped[dict] = mapped_column(JSON, default=dict)
    sync_mode: Mapped[str] = mapped_column(String(20), default=SyncMode.FULL, nullable=False)
    incremental_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    write_mode: Mapped[str] = mapped_column(String(20), default=WriteMode.UPSERT, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    retry_count: Mapped[int] = mapped_column(Integer, default=3)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    data_source: Mapped["DataSource"] = relationship(back_populates="sync_jobs")
    runs: Mapped[list["SyncJobRun"]] = relationship(back_populates="sync_job", cascade="all, delete-orphan")


class SyncJobRun(Base):
    __tablename__ = "sync_job_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sync_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("sync_jobs.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_logs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    sync_job: Mapped["SyncJob"] = relationship(back_populates="runs")
