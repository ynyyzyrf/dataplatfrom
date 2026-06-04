"""Sync job schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SyncJobCreate(BaseModel):
    data_source_id: str
    name: str = Field(..., max_length=200)
    schedule_type: str = Field(default="interval", pattern="^(interval|cron)$")
    schedule_config: dict = Field(default_factory=dict)
    sync_mode: str = Field(default="full", pattern="^(full|incremental|paged)$")
    write_mode: str = Field(default="upsert", pattern="^(insert|upsert|replace|append)$")
    is_enabled: bool = False
    timeout_seconds: int = 300
    retry_count: int = 3


class SyncJobUpdate(BaseModel):
    name: str | None = None
    schedule_type: str | None = None
    schedule_config: dict | None = None
    sync_mode: str | None = None
    write_mode: str | None = None
    is_enabled: bool | None = None
    timeout_seconds: int | None = None
    retry_count: int | None = None


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    data_source_id: str
    name: str
    schedule_type: str
    schedule_config: dict
    sync_mode: str
    write_mode: str
    is_enabled: bool
    last_run_at: str | None = None
    next_run_at: str | None = None
    timeout_seconds: int = 300
    retry_count: int = 3
    created_at: str | None = None
    updated_at: str | None = None
    last_run_status: str | None = None
    run_count: int = 0


class SyncJobRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sync_job_id: str
    status: str
    started_at: str
    finished_at: str | None = None
    fetched_count: int = 0
    inserted_count: int = 0
    failed_count: int = 0
    error_message: str | None = None
