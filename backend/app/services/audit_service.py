"""Audit log service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditService:

    async def list_logs(self, db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[AuditLog], int]:
        count_q = select(func.count(AuditLog.id))
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        logs = (await db.execute(q)).scalars().all()
        return list(logs), total
