"""Monitoring API routes — aggregated platform metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.monitoring import MonitoringOverview
from app.services.monitoring_service import MonitoringService
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])
mon_svc = MonitoringService()


@router.get("/overview", response_model=MonitoringOverview)
async def get_overview(
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    data = await mon_svc.get_overview(db)
    return MonitoringOverview(**data)
