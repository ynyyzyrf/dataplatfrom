"""Data records API — browse raw API records."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.security.authentication import get_current_user
from app.models.user import User
from app.schemas.data_record import DataRecordDetail, DataRecordListResponse, DataRecordResponse
from app.services.data_record_service import DataRecordService

router = APIRouter(prefix="/data-records", tags=["Data Records"])


@router.get("", response_model=DataRecordListResponse)
async def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    data_source_id: Optional[str] = Query(None),
    sync_job_run_id: Optional[str] = Query(None),
    response_status: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """List raw data records with optional filters."""
    service = DataRecordService()
    items, total = await service.list_records(
        db,
        page=page,
        page_size=page_size,
        data_source_id=data_source_id,
        sync_job_run_id=sync_job_run_id,
        response_status=response_status,
        start_date=start_date,
        end_date=end_date,
    )
    return DataRecordListResponse(
        items=[DataRecordResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=DataRecordDetail)
async def get_record(
    record_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single raw data record with full payload."""
    service = DataRecordService()
    record = await service.get_record(db, record_id)
    return DataRecordDetail(**record)
