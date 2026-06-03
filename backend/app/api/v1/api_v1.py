"""API v1 router — aggregator for all version-1 routes."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
