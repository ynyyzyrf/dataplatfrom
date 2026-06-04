"""Role-based access control (RBAC) helpers.

Provides FastAPI dependencies for checking the current user's roles
and permissions.
"""

from __future__ import annotations

from collections.abc import Sequence

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.user import Role, User, user_roles
from app.security.authentication import get_current_user


async def _get_user_role_names(db: AsyncSession, user_id: str) -> set[str]:
    """Fetch role names for a user."""
    result = await db.execute(
        select(Role.name)
        .join(user_roles, Role.id == user_roles.c.role_id)
        .where(user_roles.c.user_id == user_id)
    )
    return set(result.scalars().all())


def require_roles(*allowed_roles: str):
    """Return a FastAPI dependency that checks the user has at least one allowed role."""

    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
    ) -> User:
        role_names = await _get_user_role_names(db, str(user.id))
        if not role_names.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一：{', '.join(allowed_roles)}",
            )
        return user

    return checker


def require_role(role: str):
    """Shortcut for ``require_roles(role)``."""
    return require_roles(role)


async def check_permission(db: AsyncSession, user_id: str, resource: str, action: str) -> bool:
    """Check if a user has a specific permission via their roles."""
    from app.models.user import Permission, role_permissions

    result = await db.execute(
        select(Permission)
        .join(role_permissions, Permission.id == role_permissions.c.permission_id)
        .join(user_roles, role_permissions.c.role_id == user_roles.c.role_id)
        .where(
            user_roles.c.user_id == user_id,
            Permission.resource == resource,
            Permission.action == action,
        )
    )
    return result.scalar_one_or_none() is not None


def require_permission(resource: str, action: str):
    """Return a FastAPI dependency that checks for a specific permission."""

    async def checker(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db),
    ) -> User:
        allowed = await check_permission(db, str(user.id), resource, action)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限：{resource}:{action}",
            )
        return user

    return checker
