"""Role and permission management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.user import (
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleDetail,
    RoleResponse,
    RoleUpdate,
)
from app.services.role_service import RoleService
from app.security.authorization import require_roles
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["Roles"])
role_service = RoleService()


# -- Roles ------------------------------------------------------------------


@router.get("", response_model=list[RoleDetail])
async def list_roles(
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    roles = await role_service.list_roles(db)
    result = []
    for r in roles:
        user_count = await role_service.get_user_count(db, str(r.id))
        result.append(RoleDetail(
            id=r.id,
            name=r.name,
            description=r.description,
            permissions=[PermissionResponse.model_validate(p) for p in r.permissions],
            user_count=user_count,
        ))
    return result


@router.get("/{role_id}", response_model=RoleDetail)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    role = await role_service.get_role(db, role_id)
    user_count = await role_service.get_user_count(db, str(role.id))
    return RoleDetail(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[PermissionResponse.model_validate(p) for p in role.permissions],
        user_count=user_count,
    )


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    return await role_service.create_role(db, body.name, body.description)


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    updates = body.model_dump(exclude_unset=True)
    return await role_service.update_role(db, role_id, **updates)


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await role_service.delete_role(db, role_id)


# -- Permissions ------------------------------------------------------------


@router.get("/permissions/all", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin", "editor")),
):
    perms = await role_service.list_permissions(db)
    return [PermissionResponse.model_validate(p) for p in perms]


@router.post("/permissions", response_model=PermissionResponse, status_code=201)
async def create_permission(
    body: PermissionCreate,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    return await role_service.create_permission(db, body.name, body.resource, body.action)


@router.delete("/permissions/{permission_id}", status_code=204)
async def delete_permission(
    permission_id: str,
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    await role_service.delete_permission(db, permission_id)


# -- Role-Permission assignment ---------------------------------------------


@router.put("/{role_id}/permissions", response_model=RoleDetail)
async def assign_role_permissions(
    role_id: str,
    body: list[str],  # list of permission IDs
    db: AsyncSession = Depends(get_async_db),
    _current_user: User = Depends(require_roles("admin")),
):
    role = await role_service.assign_permissions(db, role_id, body)
    user_count = await role_service.get_user_count(db, str(role.id))
    return RoleDetail(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=[PermissionResponse.model_validate(p) for p in role.permissions],
        user_count=user_count,
    )
