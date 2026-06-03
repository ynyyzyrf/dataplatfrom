"""Sync job schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SyncJobCreate(BaseModel):
    data_source_id: UUID
    name: str = Field(..., max_length=200)
    schedule_type: str = Field(default="interval", pattern="^(interval|cron)$")
    schedule_config: dict = Field(default_factory=lambda: {"interval_minutes": 60})
    sync_mode: str = Field(default="full", pattern="^(full|incremental|paged)$")
    incremental_config: dict | None = None
    write_mode: str = Field(default="upsert", pattern="^(insert|upsert|replace|append)$")
    is_enabled: bool = True
    timeout_seconds: int = 300
    retry_count: int = 3


class SyncJobUpdate(BaseModel):
    name: str | None = None
    schedule_type: str | None = None
    schedule_config: dict | None = None
    sync_mode: str | None = None
    incremental_config: dict | None = None
    write_mode: str | None = None
    is_enabled: bool | None = None
    timeout_seconds: int | None = None
    retry_count: int | None = None


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_source_id: UUID
    name: str
    schedule_type: str
    schedule_config: dict
    sync_mode: str
    write_mode: str
    is_enabled: bool
    last_run_at: str | None
    next_run_at: str | None


class SyncJobRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sync_job_id: UUID
    status: str
    started_at: str
    finished_at: str | None
    fetched_count: int
    inserted_count: int
    failed_count: int
    error_message: str | None
