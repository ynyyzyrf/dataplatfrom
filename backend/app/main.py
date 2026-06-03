"""FastAPI application entry point.

Boot sequence:
1. Create the FastAPI app with metadata and CORS
2. Register lifespan (startup / shutdown) hooks
3. Mount API router under ``/api/v1``
4. Register global exception handlers
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api_v1 import router as api_v1_router
from app.config import settings
from app.core.exceptions import AppError, app_exception_handler
from app.database import async_engine

logger = logging.getLogger(__name__)


# -- Lifespan ------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("Starting %s v%s", app.title, app.version)
    yield
    logger.info("Shutting down %s", app.title)
    await async_engine.dispose()


# -- App -----------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-grade data ingestion, storage, analysis, and self-service Dashboard platform.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
app.add_exception_handler(AppError, app_exception_handler)

# Router mount
app.include_router(api_v1_router, prefix="/api/v1")


# -- Root ----------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Basic health-check endpoint."""
    return {"status": "ok", "version": settings.app_version}
