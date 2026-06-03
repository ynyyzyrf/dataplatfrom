"""Common Pydantic schemas shared across the API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    """Common response fields."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PaginationParams(BaseModel):
    """Query params for paginated endpoints."""

    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    """Wraps a list response with pagination metadata."""

    items: list
    total: int
    page: int
    page_size: int
    pages: int
