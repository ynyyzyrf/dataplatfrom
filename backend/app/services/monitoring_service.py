"""Monitoring service — aggregates metrics across the platform."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import func, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_job import SyncJob, SyncJobRun
from app.models.data_source import DataSource
from app.models.dashboard import Dashboard
from app.models.alert_rule import AlertRule


class MonitoringService:

    async def get_overview(self, db: AsyncSession) -> dict:
        """Return platform-wide monitoring overview."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Counts
        total_sources = (await db.execute(select(func.count(DataSource.id)))).scalar_one()
        total_jobs = (await db.execute(select(func.count(SyncJob.id)))).scalar_one()
        active_jobs = (await db.execute(select(func.count(SyncJob.id)).where(SyncJob.is_enabled == True))).scalar_one()
        total_dashboards = (await db.execute(select(func.count(Dashboard.id)))).scalar_one()
        active_alerts = (await db.execute(select(func.count(AlertRule.id)).where(AlertRule.is_active == True))).scalar_one()

        # Today's runs
        total_runs_today = (await db.execute(
            select(func.count(SyncJobRun.id)).where(SyncJobRun.started_at >= today_start)
        )).scalar_one()
        failed_runs_today = (await db.execute(
            select(func.count(SyncJobRun.id)).where(
                and_(SyncJobRun.started_at >= today_start, SyncJobRun.status == "failed")
            )
        )).scalar_one()

        # Per-job stats
        jobs = (await db.execute(
            select(SyncJob).order_by(SyncJob.name)
        )).scalars().all()

        job_stats = []
        for job in jobs:
            runs = (await db.execute(
                select(SyncJobRun).where(SyncJobRun.sync_job_id == job.id)
            )).scalars().all()

            total = len(runs)
            if total == 0:
                job_stats.append({
                    "sync_job_id": job.id,
                    "sync_job_name": job.name,
                    "data_source_name": None,
                    "total_runs": 0, "successful_runs": 0, "failed_runs": 0,
                    "running_runs": 0, "success_rate": 0.0,
                    "last_run_status": None, "last_run_at": None,
                    "avg_duration_ms": 0.0, "total_fetched": 0, "total_inserted": 0,
                })
                continue

            successful = sum(1 for r in runs if r.status == "success")
            failed = sum(1 for r in runs if r.status == "failed")
            running = sum(1 for r in runs if r.status == "running")

            # Duration stats
            durations = []
            for r in runs:
                if r.finished_at and r.started_at:
                    durations.append((r.finished_at - r.started_at).total_seconds() * 1000)
            avg_duration = sum(durations) / len(durations) if durations else 0.0

            # Last run
            sorted_runs = sorted(runs, key=lambda r: r.started_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
            last = sorted_runs[0] if sorted_runs else None

            ds_name = job.data_source.name if job.data_source else None

            job_stats.append({
                "sync_job_id": job.id,
                "sync_job_name": job.name,
                "data_source_name": ds_name,
                "total_runs": total,
                "successful_runs": successful,
                "failed_runs": failed,
                "running_runs": running,
                "success_rate": round(successful / total * 100, 1) if total > 0 else 0.0,
                "last_run_status": last.status if last else None,
                "last_run_at": last.started_at.isoformat() if last and last.started_at else None,
                "avg_duration_ms": round(avg_duration, 1),
                "total_fetched": sum(r.fetched_count for r in runs),
                "total_inserted": sum(r.inserted_count for r in runs),
            })

        return {
            "total_data_sources": total_sources,
            "total_sync_jobs": total_jobs,
            "active_sync_jobs": active_jobs,
            "total_dashboards": total_dashboards,
            "total_runs_today": total_runs_today,
            "failed_runs_today": failed_runs_today,
            "active_alerts": active_alerts,
            "job_stats": job_stats,
        }
