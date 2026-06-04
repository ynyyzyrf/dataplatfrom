"""Tests for role and permission management API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.models.user import Role, User
from app.services.auth_service import hash_password
from app.services.role_service import seed_default_roles


async def _get_admin_token(client: AsyncClient, db) -> str:
    """Seed defaults and login as admin. Returns token."""
    await seed_default_roles(db)
    await db.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_roles(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/roles", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3  # admin, editor, viewer
    role_names = {r["name"] for r in data}
    assert "admin" in role_names
    assert "editor" in role_names
    assert "viewer" in role_names


@pytest.mark.asyncio
async def test_create_role(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/roles", json={
        "name": "tester",
        "description": "Test role",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "tester"
    assert data["description"] == "Test role"


@pytest.mark.asyncio
async def test_create_duplicate_role(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/roles", json={
        "name": "admin",
        "description": "Duplicate",
    }, headers=headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    import sqlalchemy as sa
    viewer_role = (await db.execute(
        sa.select(Role).where(Role.name == "viewer")
    )).scalar_one()

    resp = await client.patch(f"/api/v1/roles/{viewer_role.id}", json={
        "description": "Updated description",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a role to delete
    from app.services.role_service import RoleService
    svc = RoleService()
    new_role = await svc.create_role(db, "temp_role", "Temporary")
    await db.commit()

    resp = await client.delete(f"/api/v1/roles/{new_role.id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_permissions(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/roles/permissions/all", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10
    perm_names = {p["name"] for p in data}
    assert "users:read" in perm_names
    assert "dashboards:write" in perm_names


@pytest.mark.asyncio
async def test_assign_permissions_to_role(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    import sqlalchemy as sa
    from app.models.user import Permission

    perms = (await db.execute(sa.select(Permission).limit(3))).scalars().all()
    perm_ids = [p.id for p in perms]

    resp = await client.post("/api/v1/roles", json={
        "name": "custom_role",
    }, headers=headers)
    role_id = resp.json()["id"]

    resp = await client.put(f"/api/v1/roles/{role_id}/permissions", json=perm_ids, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["permissions"]) == 3


@pytest.mark.asyncio
async def test_non_admin_cannot_manage_roles(client: AsyncClient, db):
    """Regular user without admin role cannot access role management."""
    await seed_default_roles(db)
    await db.commit()

    import sqlalchemy as sa
    viewer_role = (await db.execute(
        sa.select(Role).where(Role.name == "viewer")
    )).scalar_one()

    user = User(
        username="viewer_test",
        email="viewer_test@test.com",
        hashed_password=hash_password("viewer123"),
    )
    user.roles = [viewer_role]
    db.add(user)
    await db.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "username": "viewer_test",
        "password": "viewer123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Should be forbidden
    resp = await client.post("/api/v1/roles", json={
        "name": "hacker_role",
    }, headers=headers)
    assert resp.status_code == 403
