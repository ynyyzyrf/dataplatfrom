"""Dashboard and widget management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.dashboard import (
    DashboardCreate,
    DashboardPreview,
    DashboardResponse,
    DashboardUpdate,
    WidgetCreate,
    WidgetResponse,
    WidgetUpdate,
)
from app.schemas.dashboard_share import DashboardShareCreate, DashboardShareResponse
from app.schemas.query import QueryRequest, QueryResult
from app.schemas.common import PaginatedResponse
from app.services.dashboard_service import DashboardService
from app.services.dashboard_share_service import DashboardShareService
from app.services.query_service import QueryService
from app.security.authentication import get_current_user
from app.security.authorization import require_roles
from app.models.user import User
from app.core.exceptions import ValidationError

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])
dash_svc = DashboardService()
share_svc = DashboardShareService()
query_svc = QueryService()


def _dash_to_dict(board) -> dict:
    return DashboardResponse(
        id=board.id,
        name=board.name,
        description=board.description,
        status=board.status.value if hasattr(board.status, 'value') else str(board.status),
        visibility=board.visibility,
        created_at=board.created_at.isoformat() if board.created_at else None,
        updated_at=board.updated_at.isoformat() if board.updated_at else None,
        widget_count=len(board.widgets) if board.widgets else 0,
    ).model_dump()


# -- Dashboards ------------------------------------------------------------


@router.get("", response_model=PaginatedResponse)
async def list_dashboards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    boards, total = await dash_svc.list_dashboards(db, page=page, page_size=page_size)
    items = [_dash_to_dict(b) for b in boards]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=DashboardResponse, status_code=201)
async def create_dashboard(
    body: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    _auth: User = Depends(require_roles("admin", "editor")),
):
    board = await dash_svc.create_dashboard(db, str(current_user.id), **body.model_dump())
    return _dash_to_dict(board)


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    board = await dash_svc.get_dashboard(db, dashboard_id)
    return _dash_to_dict(board)


@router.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    body: DashboardUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    updates = body.model_dump(exclude_unset=True)
    board = await dash_svc.update_dashboard(db, dashboard_id, **updates)
    return _dash_to_dict(board)


@router.delete("/{dashboard_id}", status_code=204)
async def delete_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await dash_svc.delete_dashboard(db, dashboard_id)


# -- State machine ----------------------------------------------------------


@router.get("/{dashboard_id}/preview", response_model=DashboardPreview)
async def preview_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    """Return full render config for dashboard preview."""
    preview = await dash_svc.get_preview(db, dashboard_id)
    return DashboardPreview(**preview)


@router.post("/{dashboard_id}/publish", response_model=DashboardResponse)
async def publish_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    """Publish a draft dashboard."""
    try:
        board = await dash_svc.publish_dashboard(db, dashboard_id)
    except ValueError as e:
        raise ValidationError(str(e))
    return _dash_to_dict(board)


@router.post("/{dashboard_id}/archive", response_model=DashboardResponse)
async def archive_dashboard(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    """Archive a dashboard."""
    board = await dash_svc.archive_dashboard(db, dashboard_id)
    return _dash_to_dict(board)


# -- Widgets ---------------------------------------------------------------


@router.post("/{dashboard_id}/widgets", response_model=WidgetResponse, status_code=201)
async def add_widget(
    dashboard_id: str,
    body: WidgetCreate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    widget = await dash_svc.add_widget(db, dashboard_id, **body.model_dump())
    return WidgetResponse.model_validate(widget)


@router.patch("/widgets/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: str,
    body: WidgetUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    updates = body.model_dump(exclude_unset=True)
    widget = await dash_svc.update_widget(db, widget_id, **updates)
    return WidgetResponse.model_validate(widget)


@router.delete("/widgets/{widget_id}", status_code=204)
async def delete_widget(
    widget_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    await dash_svc.delete_widget(db, widget_id)


# -- Query -----------------------------------------------------------------


@router.post("/query", response_model=QueryResult)
async def execute_query(
    body: QueryRequest,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor", "viewer")),
):
    result = await query_svc.execute(
        db,
        table=body.table,
        dimensions=body.dimensions,
        metrics=[m.model_dump() for m in body.metrics],
        filters=[f.model_dump() for f in body.filters],
        sort=[s.model_dump() for s in body.sort],
        limit=body.limit,
        offset=body.offset,
    )
    return QueryResult(**result)


# -- Sharing ----------------------------------------------------------------


@router.get("/{dashboard_id}/shares")
async def list_shares(
    dashboard_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    """List all share records for a dashboard."""
    shares = await share_svc.list_shares(db, dashboard_id)
    return [
        DashboardShareResponse(
            id=s.id, dashboard_id=s.dashboard_id,
            shared_with_role=s.shared_with_role,
            shared_with_user_id=s.shared_with_user_id,
            permission_level=s.permission_level,
            created_by=s.created_by,
            created_at=s.created_at.isoformat() if s.created_at else None,
        ).model_dump()
        for s in shares
    ]


@router.post("/{dashboard_id}/share", status_code=201)
async def share_dashboard(
    dashboard_id: str,
    body: DashboardShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    _auth: User = Depends(require_roles("admin", "editor")),
):
    """Share a dashboard with a role or user."""
    share = await share_svc.share(db, dashboard_id, str(current_user.id), **body.model_dump())
    return DashboardShareResponse(
        id=share.id, dashboard_id=share.dashboard_id,
        shared_with_role=share.shared_with_role,
        shared_with_user_id=share.shared_with_user_id,
        permission_level=share.permission_level,
        created_by=share.created_by,
        created_at=share.created_at.isoformat() if share.created_at else None,
    ).model_dump()


@router.delete("/{dashboard_id}/shares/{share_id}", status_code=204)
async def revoke_share(
    dashboard_id: str,
    share_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    """Revoke a dashboard share."""
    await share_svc.revoke(db, share_id)
