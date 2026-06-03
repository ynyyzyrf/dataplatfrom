"""Data source schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    group: str | None
    request_method: str
    request_url: str
    auth_type: str
    headers_config: dict | None
    query_config: dict | None
    status: str
    created_at: str | None
    updated_at: str | None
