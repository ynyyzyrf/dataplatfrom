"""Monitoring metrics schemas."""

from __future__ import annotations

from pydantic import BaseModel


class JobRunStats(BaseModel):
    """Aggregated stats for a sync job."""
    sync_job_id: str
    sync_job_name: str
    data_source_name: str | None = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    running_runs: int = 0
    success_rate: float = 0.0
    last_run_status: str | None = None
    last_run_at: str | None = None
    avg_duration_ms: float = 0.0
    total_fetched: int = 0
    total_inserted: int = 0


class MonitoringOverview(BaseModel):
    """Top-level monitoring overview."""
    total_data_sources: int = 0
    total_sync_jobs: int = 0
    active_sync_jobs: int = 0
    total_dashboards: int = 0
    total_runs_today: int = 0
    failed_runs_today: int = 0
    active_alerts: int = 0
    job_stats: list[JobRunStats] = []
