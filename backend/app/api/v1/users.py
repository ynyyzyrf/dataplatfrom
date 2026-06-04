"""User management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.user import (
    AssignRoleRequest,
    RoleResponse,
    UserResponse,
    UserUpdate,
    UserWithRoles,
)
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService
from app.security.authentication import get_current_user
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


@router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    users, total = await user_service.list_users(db, page=page, page_size=page_size)
    items = []
    for u in users:
        items.append(UserWithRoles(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            roles=[r.name for r in u.roles],
        ).model_dump())
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/me", response_model=UserWithRoles)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)):
    user = await user_service.get_user(db, str(current_user.id))
    return UserWithRoles(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=[r.name for r in user.roles],
    )


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    user = await user_service.get_user(db, user_id)
    return UserWithRoles(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=[r.name for r in user.roles],
    )


@router.patch("/{user_id}", response_model=UserWithRoles)
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    updates = body.model_dump(exclude_unset=True)
    user = await user_service.update_user(db, user_id, **updates)
    return UserWithRoles(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=[r.name for r in user.roles],
    )


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await user_service.delete_user(db, user_id)


@router.put("/{user_id}/roles", response_model=UserWithRoles)
async def assign_user_roles(
    user_id: str,
    body: AssignRoleRequest,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    user = await user_service.assign_roles(db, user_id, body.role_ids)
    return UserWithRoles(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=[r.name for r in user.roles],
    )
