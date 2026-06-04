"""Audit logging middleware — captures API actions."""

from __future__ import annotations

import time
import logging
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.database import async_session_factory

logger = logging.getLogger(__name__)

# Paths to skip auditing
SKIP_PATHS = {"/api/health", "/api/docs", "/api/redoc", "/openapi.json", "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/refresh"}

RESOURCE_MAP = {
    "users": "user",
    "roles": "role",
    "data-sources": "data_source",
    "sync-jobs": "sync_job",
    "dashboards": "dashboard",
}


class AuditMiddleware(BaseHTTPMiddleware):
    """Logs API actions to the audit_logs table."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Determine if this request should be audited
        path = request.url.path
        method = request.method
        should_audit = not any(path.startswith(skip) for skip in SKIP_PATHS) and method != "GET"

        try:
            response: Response = await call_next(request)
        except Exception as e:
            response = Response(content=str(e), status_code=500)

        if should_audit and response.status_code < 500:
            await self._log_action(request, response, start_time)

        return response

    async def _log_action(self, request: Request, response: Response, start_time: float):
        """Write an audit log entry."""
        try:
            path = request.url.path
            parts = path.strip("/").split("/")

            # Determine resource type from URL
            resource_type = "unknown"
            resource_id = None
            for i, part in enumerate(parts):
                if part in RESOURCE_MAP:
                    resource_type = RESOURCE_MAP[part]
                    # Next segment is usually the resource ID
                    if i + 1 < len(parts) and parts[i + 1] not in RESOURCE_MAP:
                        resource_id = parts[i + 1]
                    break

            # Determine action from method
            action_map = {"POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}
            action = action_map.get(method := request.method, method.lower())

            # Get user ID from Authorization header
            user_id = None
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                try:
                    from jose import jwt
                    from app.config import settings
                    token = auth_header.split(" ")[1]
                    payload = jwt.decode(
                        token,
                        settings.jwt_secret.get_secret_value(),
                        algorithms=[settings.jwt_algorithm],
                    )
                    user_id = payload.get("sub")
                except Exception:
                    pass

            async with async_session_factory() as session:
                log_entry = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={
                        "method": method,
                        "path": path,
                        "status_code": response.status_code,
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                    },
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error("Failed to write audit log: %s", e)
