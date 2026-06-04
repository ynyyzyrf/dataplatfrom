"""Sync job management service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sync_job import SyncJob, SyncJobRun
from app.models.data_source import DataSource
from app.models.raw_record import RawApiRecord
from app.core.exceptions import NotFoundError, ConflictError
from app.services.datasource_service import _decrypt_auth_config

logger = logging.getLogger(__name__)


class SyncJobService:

    # -- CRUD ----------------------------------------------------------------

    async def list_jobs(self, db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[SyncJob], int]:
        count_q = select(func.count(SyncJob.id))
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(SyncJob)
            .options(selectinload(SyncJob.runs))
            .order_by(SyncJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        jobs = (await db.execute(q)).scalars().all()
        return list(jobs), total

    async def get_job(self, db: AsyncSession, job_id: str) -> SyncJob:
        q = (
            select(SyncJob)
            .options(selectinload(SyncJob.runs), selectinload(SyncJob.data_source))
            .where(SyncJob.id == job_id)
        )
        job = (await db.execute(q)).scalar_one_or_none()
        if not job:
            raise NotFoundError("同步任务未找到")
        return job

    async def create_job(self, db: AsyncSession, **kwargs) -> SyncJob:
        # Verify data source exists
        ds_q = select(DataSource).where(DataSource.id == kwargs["data_source_id"])
        ds = (await db.execute(ds_q)).scalar_one_or_none()
        if not ds:
            raise NotFoundError("数据源未找到")

        job = SyncJob(**kwargs)
        db.add(job)
        await db.flush()
        return job

    async def update_job(self, db: AsyncSession, job_id: str, **kwargs) -> SyncJob:
        job = await self.get_job(db, job_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        await db.flush()
        return await self.get_job(db, job_id)

    async def delete_job(self, db: AsyncSession, job_id: str) -> None:
        job = await self.get_job(db, job_id)
        await db.delete(job)
        await db.flush()

    # -- Execution -----------------------------------------------------------

    async def execute_job(self, db: AsyncSession, job_id: str) -> SyncJobRun:
        """Execute a sync job: fetch data from source API, store raw records."""
        job = await self.get_job(db, job_id)
        ds = job.data_source

        run = SyncJobRun(
            sync_job_id=job_id,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        await db.flush()

        try:
            # Build request config
            auth_config = _decrypt_auth_config(ds.auth_config_encrypted)
            headers = dict(ds.headers_config or {})
            params = dict(ds.query_config or {})

            if ds.auth_type == "bearer_token" and auth_config.get("token"):
                headers["Authorization"] = f"Bearer {auth_config['token']}"
            elif ds.auth_type == "api_key" and auth_config.get("key_name"):
                location = auth_config.get("key_location", "header")
                if location == "header":
                    headers[auth_config["key_name"]] = auth_config.get("key_value", "")
                elif location == "query":
                    params[auth_config["key_name"]] = auth_config.get("key_value", "")

            # Make API call
            timeout = ds.timeout_seconds or 30
            async with httpx.AsyncClient(timeout=timeout) as client:
                if ds.request_method == "POST":
                    body = dict(ds.body_config or {})
                    response = await client.post(ds.request_url, headers=headers, params=params, json=body)
                else:
                    response = await client.get(ds.request_url, headers=headers, params=params)

            # Store raw record
            raw = RawApiRecord(
                data_source_id=str(ds.id),
                sync_job_run_id=str(run.id),
                raw_payload=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"text": response.text},
                response_status=response.status_code,
            )
            db.add(raw)

            run.fetched_count = 1
            run.inserted_count = 1
            run.status = "completed"
            run.finished_at = datetime.now(timezone.utc)

        except Exception as e:
            run.status = "failed"
            run.failed_count = 1
            run.error_message = str(e)
            run.finished_at = datetime.now(timezone.utc)

        await db.flush()

        # Evaluate alert rules for this run
        try:
            from app.services.alert_service import AlertService
            from app.services.notification_service import NotificationService
            alert_svc = AlertService()
            notif_svc = NotificationService()

            triggered = await alert_svc.evaluate_for_job_run(db, run)
            for alert in triggered:
                await notif_svc.notify_admin_users(
                    db,
                    title=f"[告警] {alert['rule_name']}",
                    message=alert['message'],
                    notification_type="alert",
                    source=f"alert_rule:{alert['rule_id']}",
                )
        except Exception as alert_err:
            logger.error("Alert evaluation failed: %s", alert_err)

        return run

    async def list_runs(self, db: AsyncSession, job_id: str, page: int = 1, page_size: int = 20) -> tuple[list[SyncJobRun], int]:
        count_q = select(func.count(SyncJobRun.id)).where(SyncJobRun.sync_job_id == job_id)
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(SyncJobRun)
            .where(SyncJobRun.sync_job_id == job_id)
            .order_by(SyncJobRun.started_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        runs = (await db.execute(q)).scalars().all()
        return list(runs), total
