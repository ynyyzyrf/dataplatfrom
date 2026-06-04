"""Notification management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.notification import NotificationResponse
from app.schemas.common import PaginatedResponse
from app.services.notification_service import NotificationService
from app.security.authentication import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])
notif_svc = NotificationService()


def _notif_to_dict(n) -> dict:
    return NotificationResponse(
        id=n.id,
        user_id=n.user_id,
        title=n.title,
        message=n.message,
        notification_type=n.notification_type,
        source=n.source,
        is_read=n.is_read,
        metadata_json=n.metadata_json,
        created_at=n.created_at.isoformat() if n.created_at else None,
    ).model_dump()


@router.get("", response_model=PaginatedResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    items, total = await notif_svc.list_for_user(
        db, str(current_user.id), page=page, page_size=page_size, unread_only=unread_only,
    )
    data = [_notif_to_dict(n) for n in items]
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=data, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    count = await notif_svc.get_unread_count(db, str(current_user.id))
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    notif = await notif_svc.mark_read(db, notification_id, str(current_user.id))
    return _notif_to_dict(notif)


@router.patch("/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    count = await notif_svc.mark_all_read(db, str(current_user.id))
    return {"marked_read": count}
