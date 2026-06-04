"""Dashboard and widget management service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dashboard import Dashboard, DashboardWidget
from app.core.exceptions import NotFoundError


class DashboardService:

    # -- Dashboards ----------------------------------------------------------

    async def list_dashboards(self, db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[Dashboard], int]:
        count_q = select(func.count(Dashboard.id))
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .order_by(Dashboard.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        boards = (await db.execute(q)).scalars().all()
        return list(boards), total

    async def get_dashboard(self, db: AsyncSession, dashboard_id: str) -> Dashboard:
        q = (
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .where(Dashboard.id == dashboard_id)
        )
        board = (await db.execute(q)).scalar_one_or_none()
        if not board:
            raise NotFoundError("仪表盘未找到")
        return board

    async def create_dashboard(self, db: AsyncSession, user_id: str, **kwargs) -> Dashboard:
        board = Dashboard(created_by=user_id, **kwargs)
        db.add(board)
        await db.flush()
        # Refetch to eager-load relationships
        return await self.get_dashboard(db, str(board.id))

    async def update_dashboard(self, db: AsyncSession, dashboard_id: str, **kwargs) -> Dashboard:
        board = await self.get_dashboard(db, dashboard_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(board, key):
                setattr(board, key, value)
        await db.flush()
        return await self.get_dashboard(db, dashboard_id)

    async def delete_dashboard(self, db: AsyncSession, dashboard_id: str) -> None:
        board = await self.get_dashboard(db, dashboard_id)
        await db.delete(board)
        await db.flush()

    # -- Widgets -------------------------------------------------------------

    async def add_widget(self, db: AsyncSession, dashboard_id: str, **kwargs) -> DashboardWidget:
        # Verify dashboard exists
        await self.get_dashboard(db, dashboard_id)

        widget = DashboardWidget(dashboard_id=dashboard_id, **kwargs)
        db.add(widget)
        await db.flush()
        return widget

    async def update_widget(self, db: AsyncSession, widget_id: str, **kwargs) -> DashboardWidget:
        q = select(DashboardWidget).where(DashboardWidget.id == widget_id)
        widget = (await db.execute(q)).scalar_one_or_none()
        if not widget:
            raise NotFoundError("组件未找到")

        for key, value in kwargs.items():
            if value is not None and hasattr(widget, key):
                setattr(widget, key, value)
        await db.flush()
        return widget

    async def delete_widget(self, db: AsyncSession, widget_id: str) -> None:
        q = select(DashboardWidget).where(DashboardWidget.id == widget_id)
        widget = (await db.execute(q)).scalar_one_or_none()
        if not widget:
            raise NotFoundError("组件未找到")
        await db.delete(widget)
        await db.flush()

    # -- State machine --------------------------------------------------------

    async def publish_dashboard(self, db: AsyncSession, dashboard_id: str) -> Dashboard:
        """Transition dashboard from draft → published."""
        board = await self.get_dashboard(db, dashboard_id)
        from app.models.dashboard import DashboardStatus
        if board.status == DashboardStatus.ARCHIVED:
            raise ValueError("无法发布已归档的仪表盘")
        board.status = DashboardStatus.PUBLISHED
        await db.flush()
        return await self.get_dashboard(db, dashboard_id)

    async def archive_dashboard(self, db: AsyncSession, dashboard_id: str) -> Dashboard:
        """Archive a dashboard (only published can be archived)."""
        board = await self.get_dashboard(db, dashboard_id)
        from app.models.dashboard import DashboardStatus
        board.status = DashboardStatus.ARCHIVED
        await db.flush()
        return await self.get_dashboard(db, dashboard_id)

    async def get_preview(self, db: AsyncSession, dashboard_id: str) -> dict:
        """Return full render config for dashboard preview."""
        board = await self.get_dashboard(db, dashboard_id)
        return {
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "status": board.status.value if hasattr(board.status, 'value') else str(board.status),
            "visibility": board.visibility,
            "layout_config": board.layout_config or {},
            "widgets": [
                {
                    "id": w.id,
                    "widget_type": w.widget_type,
                    "title": w.title,
                    "component_source": w.component_source,
                    "component_key": w.component_key,
                    "component_version": w.component_version,
                    "query_config": w.query_config or {},
                    "props_config": w.props_config or {},
                    "data_binding_config": w.data_binding_config or {},
                    "event_config": w.event_config or {},
                    "visual_config": w.visual_config or {},
                    "position_config": w.position_config or {},
                }
                for w in (board.widgets or [])
            ],
            "created_at": board.created_at.isoformat() if board.created_at else None,
            "updated_at": board.updated_at.isoformat() if board.updated_at else None,
        }
