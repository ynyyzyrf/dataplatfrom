"""Auth API routes — login, register, refresh."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.user import LoginRequest, TokenRefreshRequest, TokenResponse, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.security.authentication import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    return await auth_service.authenticate(db, body.username, body.password)


@router.post("/register", response_model=UserResponse)
async def register(body: UserCreate, db: AsyncSession = Depends(get_async_db)):
    user = await auth_service.create_user(db, body.username, body.email, body.password)
    return UserResponse.model_validate(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: TokenRefreshRequest, db: AsyncSession = Depends(get_async_db)):
    return await auth_service.refresh_token(db, body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
