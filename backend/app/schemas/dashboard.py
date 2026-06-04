"""Dashboard and widget schemas."""

from __future__ import annotations

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

    id: str
    name: str
    description: str | None = None
    status: str
    visibility: str
    created_at: str | None = None
    updated_at: str | None = None
    widget_count: int = 0


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


class WidgetPreviewResponse(BaseModel):
    """Widget config as returned in dashboard preview."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    widget_type: str
    title: str
    component_source: str
    component_key: str | None = None
    component_version: str | None = None
    query_config: dict = {}
    props_config: dict = {}
    data_binding_config: dict = {}
    event_config: dict = {}
    visual_config: dict = {}
    position_config: dict = {}


class DashboardPreview(BaseModel):
    """Full dashboard render config for preview."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    status: str
    visibility: str
    layout_config: dict = {}
    widgets: list[WidgetPreviewResponse] = []
    created_at: str | None = None
    updated_at: str | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dashboard_id: str
    widget_type: str
    title: str
    component_source: str
    component_key: str | None = None
    component_version: str | None = None
    query_config: dict | None = None
    props_config: dict | None = None
    position_config: dict | None = None
