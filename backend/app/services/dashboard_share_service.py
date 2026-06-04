"""Dashboard sharing service."""

from __future__ import annotations

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dashboard import Dashboard
from app.models.dashboard_share import DashboardShare
from app.core.exceptions import NotFoundError


class DashboardShareService:

    async def list_shares(self, db: AsyncSession, dashboard_id: str) -> list[DashboardShare]:
        q = select(DashboardShare).where(DashboardShare.dashboard_id == dashboard_id)
        result = (await db.execute(q)).scalars().all()
        return list(result)

    async def share(self, db: AsyncSession, dashboard_id: str, created_by: str, **kwargs) -> DashboardShare:
        # Verify dashboard exists
        dash_q = select(Dashboard).where(Dashboard.id == dashboard_id)
        dash = (await db.execute(dash_q)).scalar_one_or_none()
        if not dash:
            raise NotFoundError("仪表盘未找到")

        # Check for duplicate share
        role = kwargs.get("shared_with_role")
        user_id = kwargs.get("shared_with_user_id")
        dup_q = select(DashboardShare).where(
            and_(
                DashboardShare.dashboard_id == dashboard_id,
                DashboardShare.shared_with_role == role,
                DashboardShare.shared_with_user_id == user_id,
            )
        )
        existing = (await db.execute(dup_q)).scalar_one_or_none()
        if existing:
            # Update permission level
            existing.permission_level = kwargs.get("permission_level", "view")
            await db.flush()
            return existing

        share = DashboardShare(dashboard_id=dashboard_id, created_by=created_by, **kwargs)
        db.add(share)
        await db.flush()
        return share

    async def revoke(self, db: AsyncSession, share_id: str) -> None:
        q = select(DashboardShare).where(DashboardShare.id == share_id)
        share = (await db.execute(q)).scalar_one_or_none()
        if not share:
            raise NotFoundError("分享记录未找到")
        await db.delete(share)
        await db.flush()

    async def get_accessible_dashboards(self, db: AsyncSession, user_id: str, user_roles: list[str]) -> list[str]:
        """Return list of dashboard IDs a user can access (via sharing + roles)."""
        # Dashboards where the user is the creator
        owned_q = select(Dashboard.id).where(Dashboard.created_by == user_id)
        owned = (await db.execute(owned_q)).scalars().all()

        # Dashboards shared with the user directly
        user_shared_q = select(DashboardShare.dashboard_id).where(
            DashboardShare.shared_with_user_id == user_id
        )
        user_shared = (await db.execute(user_shared_q)).scalars().all()

        # Dashboards shared with any of the user's roles
        role_shared_q = select(DashboardShare.dashboard_id).where(
            DashboardShare.shared_with_role.in_(user_roles)
        )
        role_shared = (await db.execute(role_shared_q)).scalars().all()

        return list(set(owned + user_shared + role_shared))
