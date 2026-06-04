"""Tests for user management API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import Role, User
from app.services.auth_service import hash_password
from app.services.role_service import seed_default_roles


async def _setup_admin(client: AsyncClient, db) -> str:
    """Seed defaults and login as admin. Returns token."""
    await seed_default_roles(db)
    await db.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    return resp.json()["access_token"]


async def _register_and_login(client: AsyncClient, username: str = "admin1", password: str = "admin123") -> str:
    """Helper: register a user and return access token."""
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password,
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_users_empty(client: AsyncClient):
    token = await _register_and_login(client, "admin1")
    headers = {"Authorization": f"Bearer {token}"}
    # Without admin role, this should be forbidden
    resp = await client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    token = await _register_and_login(client, "testuser")
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@test.com"
    assert "roles" in data


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_list_users(client: AsyncClient, db):
    """Admin user should be able to list all users."""
    token = await _setup_admin(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_admin_can_update_user(client: AsyncClient, db):
    token = await _setup_admin(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a regular user to update
    import sqlalchemy as sa
    user = User(
        username="regular_u",
        email="regular_u@test.com",
        hashed_password=hash_password("user123"),
    )
    db.add(user)
    await db.commit()

    # Update user
    resp = await client.patch(f"/api/v1/users/{user.id}", json={
        "is_active": False,
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_admin_can_assign_roles(client: AsyncClient, db):
    token = await _setup_admin(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    import sqlalchemy as sa
    viewer_role = (await db.execute(
        sa.select(Role).where(Role.name == "viewer")
    )).scalar_one()

    user = User(
        username="tobeviewer",
        email="tobeviewer@test.com",
        hashed_password=hash_password("user123"),
    )
    db.add(user)
    await db.commit()

    # Assign viewer role
    resp = await client.put(f"/api/v1/users/{user.id}/roles", json={
        "role_ids": [str(viewer_role.id)],
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "viewer" in data["roles"]


@pytest.mark.asyncio
async def test_admin_can_delete_user(client: AsyncClient, db):
    token = await _setup_admin(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    import sqlalchemy as sa
    user = User(
        username="todelete",
        email="todelete@test.com",
        hashed_password=hash_password("user123"),
    )
    db.add(user)
    await db.commit()

    # Delete user
    resp = await client.delete(f"/api/v1/users/{user.id}", headers=headers)
    assert resp.status_code == 204
