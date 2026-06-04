"""FastAPI application entry point.

Boot sequence:
1. Create the FastAPI app with metadata and CORS
2. Register lifespan (startup / shutdown) hooks
3. Mount API router under ``/api/v1``
4. Mount frontend SPA static files (production builds only)
5. Register global exception handlers
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from app.api.v1.api_v1 import router as api_v1_router
from app.config import settings
from app.core.exceptions import AppError, app_exception_handler
from app.database import Base, async_engine, async_session_factory
from app.middleware.audit import AuditMiddleware
from app.services.role_service import seed_default_roles

logger = logging.getLogger(__name__)

# Path to the production frontend build
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# -- Lifespan ------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("Starting %s v%s", app.title, app.version)

    # Auto-create tables and seed default roles/permissions
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await seed_default_roles(session)
        await session.commit()

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

# Audit logging (before global exception handler)
app.add_middleware(AuditMiddleware)

# Global exception handler
app.add_exception_handler(AppError, app_exception_handler)

# Router mount
app.include_router(api_v1_router, prefix="/api/v1")


# -- API health / root ---------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Basic health-check endpoint."""
    return {"status": "ok", "version": settings.app_version}


# -- Frontend SPA (production only) --------------------------------------
# The `static/` directory is populated by the Docker multi-stage build.
# In local dev the frontend is served by Vite's dev server; this block is
# a no-op when the directory doesn't exist.

if STATIC_DIR.is_dir():
    logger.info("Serving frontend SPA from %s", STATIC_DIR)

    # Serve hashed assets (JS / CSS / images) with long-cache-friendly URLs
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    # Serve individual root-level static files (favicon, icons, etc.)
    _ROOT_STATIC_FILES = {
        "favicon.svg": "favicon.svg",
        "icons.svg": "icons.svg",
    }

    def _make_static_route(filepath: Path):
        """Factory to avoid closure‑over‑loop‑variable pitfalls."""

        async def _handler() -> FileResponse:
            return FileResponse(str(filepath))

        return _handler

    for url_path, filename in _ROOT_STATIC_FILES.items():
        fp = STATIC_DIR / filename
        if fp.exists():
            app.get(f"/{url_path}", name=url_path)(_make_static_route(fp))

    # SPA catch-all — every non-API path returns index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Catch-all: serve index.html for any unmatched path (SPA routing)."""
        return FileResponse(str(STATIC_DIR / "index.html"))

else:
    logger.info(
        "No static/ directory found — frontend SPA is disabled. "
        "Run the Docker multi-stage build or use Vite dev server during development."
    )
