"""Data record schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class DataRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    data_source_id: str
    data_source_name: str | None = None
    sync_job_run_id: str | None = None
    response_status: int | None = None
    fetched_at: datetime | None = None
    created_at: datetime | None = None
    payload_preview: str | None = None  # first 200 chars of raw_payload

    @field_serializer("fetched_at", "created_at")
    def serialize_dt(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.isoformat()


class DataRecordDetail(DataRecordResponse):
    raw_payload: dict | list | None = None


class DataRecordListResponse(BaseModel):
    items: list[DataRecordResponse]
    total: int
    page: int
    page_size: int
