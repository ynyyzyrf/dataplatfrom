"""Dashboard share schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DashboardShareCreate(BaseModel):
    shared_with_role: str | None = None
    shared_with_user_id: str | None = None
    permission_level: str = "view"


class DashboardShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dashboard_id: str
    shared_with_role: str | None = None
    shared_with_user_id: str | None = None
    permission_level: str
    created_by: str
    created_at: str | None = None
