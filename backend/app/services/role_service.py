"""Role and permission management service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import Permission, Role, User, role_permissions, user_roles
from app.core.exceptions import ConflictError, NotFoundError


class RoleService:

    # -- Roles ---------------------------------------------------------------

    async def list_roles(self, db: AsyncSession) -> list[Role]:
        """List all roles with permissions."""
        q = select(Role).options(selectinload(Role.permissions)).order_by(Role.name)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def get_role(self, db: AsyncSession, role_id: str) -> Role:
        """Get a single role with permissions."""
        q = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        role = (await db.execute(q)).scalar_one_or_none()
        if not role:
            raise NotFoundError("角色未找到")
        return role

    async def create_role(self, db: AsyncSession, name: str, description: str | None = None) -> Role:
        """Create a new role."""
        existing = await db.execute(select(Role).where(Role.name == name))
        if existing.scalar_one_or_none():
            raise ConflictError(f"角色'{name}'已存在")

        role = Role(name=name, description=description)
        db.add(role)
        await db.flush()
        return role

    async def update_role(self, db: AsyncSession, role_id: str, **kwargs) -> Role:
        """Update a role."""
        role = await self.get_role(db, role_id)

        if "name" in kwargs and kwargs["name"]:
            existing = await db.execute(
                select(Role).where(Role.name == kwargs["name"], Role.id != role_id)
            )
            if existing.scalar_one_or_none():
                raise ConflictError(f"角色名称'{kwargs['name']}'已被占用")

        for key, value in kwargs.items():
            if value is not None and hasattr(role, key):
                setattr(role, key, value)

        await db.flush()
        return await self.get_role(db, role_id)

    async def delete_role(self, db: AsyncSession, role_id: str) -> None:
        """Delete a role."""
        role = await self.get_role(db, role_id)
        await db.delete(role)
        await db.flush()

    async def get_user_count(self, db: AsyncSession, role_id: str) -> int:
        result = await db.execute(
            select(func.count()).select_from(user_roles).where(user_roles.c.role_id == role_id)
        )
        return result.scalar_one()

    # -- Permissions ---------------------------------------------------------

    async def list_permissions(self, db: AsyncSession) -> list[Permission]:
        """List all permissions."""
        q = select(Permission).order_by(Permission.resource, Permission.action)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def create_permission(self, db: AsyncSession, name: str, resource: str, action: str) -> Permission:
        """Create a new permission."""
        existing = await db.execute(select(Permission).where(Permission.name == name))
        if existing.scalar_one_or_none():
            raise ConflictError(f"权限'{name}'已存在")

        perm = Permission(name=name, resource=resource, action=action)
        db.add(perm)
        await db.flush()
        return perm

    async def delete_permission(self, db: AsyncSession, permission_id: str) -> None:
        """Delete a permission."""
        perm = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        perm = perm.scalar_one_or_none()
        if not perm:
            raise NotFoundError("权限未找到")
        await db.delete(perm)
        await db.flush()

    async def assign_permissions(self, db: AsyncSession, role_id: str, permission_ids: list[str]) -> Role:
        """Assign permissions to a role (replaces existing)."""
        role = await self.get_role(db, role_id)

        if permission_ids:
            q = select(Permission).where(Permission.id.in_(permission_ids))
            perms = (await db.execute(q)).scalars().all()
            if len(perms) != len(permission_ids):
                raise NotFoundError("一个或多个权限未找到")
            role.permissions = list(perms)
        else:
            role.permissions = []

        await db.flush()
        return await self.get_role(db, role_id)


# -- Seed default roles -----------------------------------------------------


async def seed_default_roles(db: AsyncSession) -> None:
    """Create default roles and permissions if they don't exist."""
    # Default permissions
    default_permissions = [
        ("users:read", "users", "read"),
        ("users:write", "users", "write"),
        ("roles:read", "roles", "read"),
        ("roles:write", "roles", "write"),
        ("datasources:read", "datasources", "read"),
        ("datasources:write", "datasources", "write"),
        ("syncjobs:read", "syncjobs", "read"),
        ("syncjobs:write", "syncjobs", "write"),
        ("syncjobs:execute", "syncjobs", "execute"),
        ("dashboards:read", "dashboards", "read"),
        ("dashboards:write", "dashboards", "write"),
        ("audit:read", "audit", "read"),
    ]

    perms_map: dict[str, Permission] = {}
    for perm_name, resource, action in default_permissions:
        existing = await db.execute(select(Permission).where(Permission.name == perm_name))
        perm = existing.scalar_one_or_none()
        if not perm:
            perm = Permission(name=perm_name, resource=resource, action=action)
            db.add(perm)
            await db.flush()
        perms_map[perm_name] = perm

    # Default roles
    existing_admin = await db.execute(select(Role).where(Role.name == "admin"))
    if not existing_admin.scalar_one_or_none():
        admin = Role(name="admin", description="系统完全访问权限")
        admin.permissions = list(perms_map.values())
        db.add(admin)

    existing_editor = await db.execute(select(Role).where(Role.name == "editor"))
    if not existing_editor.scalar_one_or_none():
        editor = Role(name="editor", description="可管理数据源、同步任务和仪表盘")
        editor.permissions = [
            perms_map[k] for k in [
                "datasources:read", "datasources:write",
                "syncjobs:read", "syncjobs:write", "syncjobs:execute",
                "dashboards:read", "dashboards:write",
                "audit:read",
                "users:read",
            ]
        ]
        db.add(editor)

    existing_viewer = await db.execute(select(Role).where(Role.name == "viewer"))
    if not existing_viewer.scalar_one_or_none():
        viewer = Role(name="viewer", description="仪表盘和数据的只读访问权限")
        viewer.permissions = [
            perms_map[k] for k in [
                "dashboards:read",
                "datasources:read",
                "syncjobs:read",
            ]
        ]
        db.add(viewer)

    await db.flush()

    # Create default admin user if no admin exists; ensure admin has admin role
    from app.models.user import User
    from app.services.auth_service import hash_password

    admin_role = await db.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one()

    admin_user = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.username == "admin")
    )
    admin_user = admin_user.scalar_one_or_none()

    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@gdp.local",
            hashed_password=hash_password("admin123"),
            is_active=True,
        )
        admin_user.roles = [admin_role]
        db.add(admin_user)
    elif not admin_user.roles:
        admin_user.roles = [admin_role]
