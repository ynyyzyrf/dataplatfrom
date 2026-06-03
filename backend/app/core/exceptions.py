"""Global exception handlers and application exceptions.

Collects domain-specific exceptions so API layers can raise typed errors
instead of returning raw HTTP 500 responses.
"""

from __future__ import annotations

from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# -- Domain exceptions ---------------------------------------------------


class AppError(Exception):
    """Base application error with an HTTP status code."""

    def __init__(
        self,
        message: str = "Application error",
        status_code: HTTPStatus | int = HTTPStatus.INTERNAL_SERVER_ERROR,
        detail: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=HTTPStatus.NOT_FOUND)


class UnauthorizedError(AppError):
    """Authentication or authorization failed."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=HTTPStatus.UNAUTHORIZED)


class ConflictError(AppError):
    """Resource already exists or conflict."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, status_code=HTTPStatus.CONFLICT)


class ValidationError(AppError):
    """Business logic validation failed."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message=message, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


# -- Response schema -----------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard API error response body."""

    detail: str
    code: str | None = None


# -- FastAPI handler -----------------------------------------------------


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.detail.get("code"), **exc.detail},
    )
