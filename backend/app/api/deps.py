"""FastAPI dependency injection helpers."""

from __future__ import annotations

from app.database import get_async_db
from app.security.authentication import get_current_user
