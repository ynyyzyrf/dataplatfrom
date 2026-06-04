"""Data source schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class DataSourceCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    group: str | None = None
    request_method: str = Field(default="GET", pattern="^(GET|POST)$")
    request_url: str = Field(..., min_length=1)
    auth_type: str = Field(default="none", pattern="^(none|bearer_token|api_key)$")
    auth_config: dict | None = None
    headers_config: dict | None = None
    query_config: dict | None = None
    body_config: dict | None = None
    timeout_seconds: int = 30
    retry_count: int = 3


class DataSourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    group: str | None = None
    request_method: str | None = None
    request_url: str | None = None
    auth_type: str | None = None
    auth_config: dict | None = None
    headers_config: dict | None = None
    query_config: dict | None = None
    body_config: dict | None = None
    timeout_seconds: int | None = None
    retry_count: int | None = None
    status: str | None = None


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    group: str | None = None
    request_method: str
    request_url: str
    auth_type: str
    headers_config: dict | None = None
    query_config: dict | None = None
    body_config: dict | None = None
    timeout_seconds: int = 30
    retry_count: int = 3
    status: str
    created_by: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime | None) -> str | None:
        if dt is None:
            return None
        return dt.isoformat()


class DataSourceDetail(DataSourceResponse):
    auth_config: dict | None = None
    sync_job_count: int = 0
