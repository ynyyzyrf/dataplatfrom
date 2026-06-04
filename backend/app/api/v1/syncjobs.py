"""Sync job management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.sync_job import (
    SyncJobCreate,
    SyncJobResponse,
    SyncJobRunResponse,
    SyncJobUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.syncjob_service import SyncJobService
from app.security.authentication import get_current_user
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/sync-jobs", tags=["Sync Jobs"])
svc = SyncJobService()


def _job_to_response(job) -> dict:
    return SyncJobResponse(
        id=job.id,
        data_source_id=job.data_source_id,
        name=job.name,
        schedule_type=job.schedule_type,
        schedule_config=job.schedule_config,
        sync_mode=job.sync_mode,
        write_mode=job.write_mode,
        is_enabled=job.is_enabled,
        last_run_at=job.last_run_at.isoformat() if job.last_run_at else None,
        next_run_at=job.next_run_at.isoformat() if job.next_run_at else None,
        timeout_seconds=job.timeout_seconds,
        retry_count=job.retry_count,
        created_at=job.created_at.isoformat() if job.created_at else None,
        updated_at=job.updated_at.isoformat() if job.updated_at else None,
        last_run_status=job.runs[0].status if job.runs else None,
        run_count=len(job.runs) if job.runs else 0,
    ).model_dump()


@router.get("", response_model=PaginatedResponse)
async def list_sync_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    jobs, total = await svc.list_jobs(db, page=page, page_size=page_size)
    items = [_job_to_response(j) for j in jobs]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=SyncJobResponse, status_code=201)
async def create_sync_job(
    body: SyncJobCreate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    job = await svc.create_job(db, **body.model_dump())
    # Reload with relations
    job = await svc.get_job(db, str(job.id))
    return _job_to_response(job)


@router.get("/{job_id}", response_model=SyncJobResponse)
async def get_sync_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    job = await svc.get_job(db, job_id)
    return _job_to_response(job)


@router.patch("/{job_id}", response_model=SyncJobResponse)
async def update_sync_job(
    job_id: str,
    body: SyncJobUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    updates = body.model_dump(exclude_unset=True)
    job = await svc.update_job(db, job_id, **updates)
    return _job_to_response(job)


@router.delete("/{job_id}", status_code=204)
async def delete_sync_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await svc.delete_job(db, job_id)


@router.post("/{job_id}/execute", response_model=SyncJobRunResponse)
async def execute_sync_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    run = await svc.execute_job(db, job_id)
    return SyncJobRunResponse(
        id=run.id,
        sync_job_id=run.sync_job_id,
        status=run.status,
        started_at=run.started_at.isoformat(),
        finished_at=run.finished_at.isoformat() if run.finished_at else None,
        fetched_count=run.fetched_count,
        inserted_count=run.inserted_count,
        failed_count=run.failed_count,
        error_message=run.error_message,
    )


@router.get("/{job_id}/runs", response_model=PaginatedResponse)
async def list_sync_job_runs(
    job_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    runs, total = await svc.list_runs(db, job_id, page=page, page_size=page_size)
    items = [
        SyncJobRunResponse(
            id=r.id,
            sync_job_id=r.sync_job_id,
            status=r.status,
            started_at=r.started_at.isoformat(),
            finished_at=r.finished_at.isoformat() if r.finished_at else None,
            fetched_count=r.fetched_count,
            inserted_count=r.inserted_count,
            failed_count=r.failed_count,
            error_message=r.error_message,
        ).model_dump()
        for r in runs
    ]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)
