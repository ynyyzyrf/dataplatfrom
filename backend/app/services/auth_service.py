"""Authentication and user service."""

from __future__ import annotations

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.security.authentication import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedError, ConflictError, NotFoundError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


class AuthService:

    async def authenticate(self, db: AsyncSession, username: str, password: str) -> dict:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("用户名或密码错误")
        if not user.is_active:
            raise UnauthorizedError("用户账户已停用")

        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "bearer",
        }

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("令牌类型无效")

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedError("用户未找到或已停用")

        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
            "token_type": "bearer",
        }

    async def create_user(self, db: AsyncSession, username: str, email: str, password: str) -> User:
        existing = await db.execute(select(User).where((User.username == username) | (User.email == email)))
        if existing.scalar_one_or_none():
            raise ConflictError("用户名或邮箱已存在")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
        await db.flush()
        return user

    async def get_user(self, db: AsyncSession, user_id: str) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("用户未找到")
        return user
