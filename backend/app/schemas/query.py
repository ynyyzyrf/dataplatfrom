"""Query service schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MetricConfig(BaseModel):
    field: str
    aggregation: str = Field(default="sum", pattern="^(count|sum|avg|max|min|distinct_count)$")
    alias: str | None = None


class FilterConfig(BaseModel):
    field: str
    operator: str = Field(default="=", pattern="^(=|!=|>|<|>=|<=|in|not_in|like|contains)$")
    value: str | int | float | list | None = None


class SortConfig(BaseModel):
    field: str
    direction: str = Field(default="asc", pattern="^(asc|desc)$")


class QueryRequest(BaseModel):
    table: str
    dimensions: list[str] = Field(default_factory=list)
    metrics: list[MetricConfig] = Field(default_factory=list)
    filters: list[FilterConfig] = Field(default_factory=list)
    sort: list[SortConfig] = Field(default_factory=list)
    time_range: dict | None = None
    limit: int = 100
    offset: int = 0


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list]
    total: int
