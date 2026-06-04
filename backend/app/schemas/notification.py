"""Notification schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    source: str | None = None
    is_read: bool
    metadata_json: dict | None = None
    created_at: str | None = None
