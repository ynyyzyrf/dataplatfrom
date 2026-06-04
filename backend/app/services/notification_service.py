"""Notification service for in-app and multi-channel notifications."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class NotificationService:

    async def list_for_user(
        self, db: AsyncSession, user_id: str,
        page: int = 1, page_size: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        conditions = [Notification.user_id == user_id]
        if unread_only:
            conditions.append(Notification.is_read == False)

        count_q = select(func.count(Notification.id)).where(*conditions)
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(Notification)
            .where(*conditions)
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        notifications = (await db.execute(q)).scalars().all()
        return list(notifications), total

    async def get_unread_count(self, db: AsyncSession, user_id: str) -> int:
        q = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        return (await db.execute(q)).scalar_one()

    async def mark_read(self, db: AsyncSession, notification_id: str, user_id: str) -> Notification:
        q = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        notif = (await db.execute(q)).scalar_one_or_none()
        if not notif:
            raise NotFoundError("通知未找到")
        notif.is_read = True
        await db.flush()
        return notif

    async def mark_all_read(self, db: AsyncSession, user_id: str) -> int:
        q = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        notifs = (await db.execute(q)).scalars().all()
        count = 0
        for n in notifs:
            n.is_read = True
            count += 1
        await db.flush()
        return count

    async def create_notification(
        self, db: AsyncSession, user_id: str,
        title: str, message: str,
        notification_type: str = "alert",
        source: str | None = None,
        metadata_json: dict | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            source=source,
            metadata_json=metadata_json,
        )
        db.add(notif)
        await db.flush()
        return notif

    async def notify_admin_users(
        self, db: AsyncSession,
        title: str, message: str,
        notification_type: str = "alert",
        source: str | None = None,
    ) -> list[Notification]:
        """Send notification to all admin users."""
        q = select(User).join(User.roles).where(User.roles.any(name="admin"))
        admins = (await db.execute(q)).scalars().all()
        notifications = []
        for admin in admins:
            notif = await self.create_notification(
                db, str(admin.id), title, message,
                notification_type=notification_type, source=source,
            )
            notifications.append(notif)
        return notifications
