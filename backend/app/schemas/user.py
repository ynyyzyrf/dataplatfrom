"""Auth and user schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -- Auth -------------------------------------------------------------------


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


# -- User -------------------------------------------------------------------


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    is_active: bool


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None


class UserWithRoles(UserResponse):
    roles: list[str] = []


# -- Role -------------------------------------------------------------------


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None


class RoleDetail(RoleResponse):
    permissions: list["PermissionResponse"] = []
    user_count: int = 0


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class AssignRoleRequest(BaseModel):
    role_ids: list[str]


# -- Permission -------------------------------------------------------------


class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    resource: str = Field(..., min_length=2, max_length=50)
    action: str = Field(..., min_length=2, max_length=20)


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    resource: str
    action: str
