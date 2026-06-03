"""Role-based access control (RBAC) helpers.

Provides FastAPI dependencies for checking the current user's roles
and permissions.
"""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.user import Role, User, user_roles
from app.security.authentication import get_current_user


def require_roles(*allowed_roles: str) -> object:
    """Return a callable that checks if the user has at least one allowed role."""

    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
    ) -> User:
        result = await db.execute(
            user_roles.select().where(user_roles.c.user_id == user.id)
        )
        user_roles_row = result.scalars().all()
        user_roles_names = {r.role.name for r in user_roles_row}
        if not user_roles_names.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return user

    return checker  # type: ignore[return-value]


def require_role(role: str):
    """Shortcut for ``require_roles(role)``."""
    return require_roles(role)
