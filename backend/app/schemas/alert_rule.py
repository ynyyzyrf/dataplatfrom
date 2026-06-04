"""Alert rule schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AlertRuleCreate(BaseModel):
    name: str = Field(..., max_length=200)
    rule_type: str = Field(..., max_length=50)
    target_type: str = Field(..., max_length=50)
    target_id: str | None = None
    threshold: int = 1
    window_minutes: int = 15
    channels: list[str] = ["in_app"]
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    name: str | None = None
    rule_type: str | None = None
    target_type: str | None = None
    target_id: str | None = None
    threshold: int | None = None
    window_minutes: int | None = None
    channels: list[str] | None = None
    is_active: bool | None = None


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    rule_type: str
    target_type: str
    target_id: str | None = None
    threshold: int
    window_minutes: int
    channels: list = []
    is_active: bool
    created_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
