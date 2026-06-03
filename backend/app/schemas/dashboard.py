"""Dashboard schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    layout_config: dict | None = None
    visibility: str = "private"


class DashboardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    layout_config: dict | None = None
    visibility: str | None = None
    status: str | None = None


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    status: str
    visibility: str
    created_at: str | None
    updated_at: str | None


class WidgetCreate(BaseModel):
    widget_type: str
    title: str = Field(..., max_length=200)
    component_source: str = "system"
    component_key: str | None = None
    component_version: str | None = None
    query_config: dict | None = None
    props_config: dict | None = None
    data_binding_config: dict | None = None
    event_config: dict | None = None
    visual_config: dict | None = None
    position_config: dict | None = None


class WidgetUpdate(BaseModel):
    title: str | None = None
    query_config: dict | None = None
    props_config: dict | None = None
    data_binding_config: dict | None = None
    event_config: dict | None = None
    visual_config: dict | None = None
    position_config: dict | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dashboard_id: UUID
    widget_type: str
    title: str
    component_source: str
    component_key: str | None
    component_version: str | None
    query_config: dict | None
    props_config: dict | None
    position_config: dict | None
