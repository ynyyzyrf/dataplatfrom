"""User management service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import Permission, Role, User, user_roles
from app.core.exceptions import ConflictError, NotFoundError
from app.services.auth_service import hash_password


class UserService:

    async def list_users(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        """List users with pagination."""
        count_q = select(func.count(User.id))
        total = (await db.execute(count_q)).scalar_one()

        q = (
            select(User)
            .options(selectinload(User.roles))
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        users = (await db.execute(q)).scalars().all()
        return list(users), total

    async def get_user(self, db: AsyncSession, user_id: str) -> User:
        """Get a single user with roles."""
        q = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = (await db.execute(q)).scalar_one_or_none()
        if not user:
            raise NotFoundError("用户未找到")
        return user

    async def update_user(self, db: AsyncSession, user_id: str, **kwargs) -> User:
        """Update user fields (email, is_active, etc.)."""
        user = await self.get_user(db, user_id)

        if "username" in kwargs:
            existing = await db.execute(
                select(User).where(User.username == kwargs["username"], User.id != user_id)
            )
            if existing.scalar_one_or_none():
                raise ConflictError("用户名已被占用")

        if "email" in kwargs and kwargs["email"]:
            existing = await db.execute(
                select(User).where(User.email == kwargs["email"], User.id != user_id)
            )
            if existing.scalar_one_or_none():
                raise ConflictError("邮箱已被占用")

        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        await db.flush()
        return await self.get_user(db, user_id)

    async def delete_user(self, db: AsyncSession, user_id: str) -> None:
        """Delete a user."""
        user = await self.get_user(db, user_id)
        await db.delete(user)
        await db.flush()

    async def assign_roles(self, db: AsyncSession, user_id: str, role_ids: list[str]) -> User:
        """Assign roles to a user (replaces existing roles)."""
        user = await self.get_user(db, user_id)

        # Verify all roles exist
        if role_ids:
            q = select(Role).where(Role.id.in_(role_ids))
            roles = (await db.execute(q)).scalars().all()
            if len(roles) != len(role_ids):
                raise NotFoundError("一个或多个角色未找到")
            user.roles = list(roles)
        else:
            user.roles = []

        await db.flush()
        return await self.get_user(db, user_id)

    async def get_user_roles(self, db: AsyncSession, user_id: str) -> list[Role]:
        """Get roles for a user."""
        user = await self.get_user(db, user_id)
        return list(user.roles)
