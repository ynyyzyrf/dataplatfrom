"""API v1 router — aggregator for all version-1 routes."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.datasources import router as datasources_router
from app.api.v1.syncjobs import router as syncjobs_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.audit import router as audit_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.data_records import router as data_records_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(datasources_router)
router.include_router(syncjobs_router)
router.include_router(dashboards_router)
router.include_router(audit_router)
router.include_router(alerts_router)
router.include_router(notifications_router)
router.include_router(monitoring_router)
router.include_router(data_records_router)
