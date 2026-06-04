"""Data source management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceDetail,
    DataSourceResponse,
    DataSourceUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.datasource_service import DataSourceService
from app.security.authentication import get_current_user
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/data-sources", tags=["Data Sources"])
ds_service = DataSourceService()


@router.get("", response_model=PaginatedResponse)
async def list_data_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    sources, total = await ds_service.list_sources(db, page=page, page_size=page_size)
    items = [DataSourceResponse.model_validate(s).model_dump() for s in sources]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=DataSourceResponse, status_code=201)
async def create_data_source(
    body: DataSourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    _auth: User = Depends(require_roles("admin", "editor")),
):
    source = await ds_service.create_source(db, str(current_user.id), **body.model_dump())
    return DataSourceResponse.model_validate(source)


@router.get("/{source_id}", response_model=DataSourceDetail)
async def get_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    source = await ds_service.get_source(db, source_id)
    auth_config = await ds_service.get_decrypted_config(source)
    sync_count = len(source.sync_jobs) if source.sync_jobs else 0
    return DataSourceDetail(
        **DataSourceResponse.model_validate(source).model_dump(),
        auth_config=auth_config,
        sync_job_count=sync_count,
    )


@router.patch("/{source_id}", response_model=DataSourceResponse)
async def update_data_source(
    source_id: str,
    body: DataSourceUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    updates = body.model_dump(exclude_unset=True)
    source = await ds_service.update_source(db, source_id, **updates)
    return DataSourceResponse.model_validate(source)


@router.delete("/{source_id}", status_code=204)
async def delete_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await ds_service.delete_source(db, source_id)
