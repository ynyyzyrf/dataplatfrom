"""Tests for data source management API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.role_service import seed_default_roles


async def _get_admin_token(client: AsyncClient, db) -> str:
    """Seed defaults and login as admin."""
    await seed_default_roles(db)
    await db.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_data_sources_empty(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/data-sources", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_data_source(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/data-sources", json={
        "name": "Test API",
        "request_url": "https://jsonplaceholder.typicode.com/posts",
        "request_method": "GET",
        "auth_type": "none",
        "description": "A test data source",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test API"
    assert data["request_url"] == "https://jsonplaceholder.typicode.com/posts"
    assert data["auth_type"] == "none"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_create_data_source_with_auth(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/data-sources", json={
        "name": "Secure API",
        "request_url": "https://api.example.com/data",
        "request_method": "GET",
        "auth_type": "bearer_token",
        "auth_config": {"token": "secret-token-123"},
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Secure API"
    # Auth config should NOT be in the basic response
    assert "auth_config" not in data or data.get("auth_config") is None


@pytest.mark.asyncio
async def test_get_data_source_detail(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post("/api/v1/data-sources", json={
        "name": "Detail Test",
        "request_url": "https://api.example.com/data",
        "request_method": "POST",
        "auth_type": "api_key",
        "auth_config": {"key_name": "X-API-Key", "key_value": "abc123"},
    }, headers=headers)
    source_id = resp.json()["id"]

    # Get detail
    resp = await client.get(f"/api/v1/data-sources/{source_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Detail Test"
    assert data["auth_config"] is not None
    assert data["auth_config"]["key_name"] == "X-API-Key"
    assert data["auth_config"]["key_value"] == "abc123"


@pytest.mark.asyncio
async def test_update_data_source(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/data-sources", json={
        "name": "Old Name",
        "request_url": "https://old.example.com",
    }, headers=headers)
    source_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/data-sources/{source_id}", json={
        "name": "New Name",
        "description": "Updated description",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_data_source(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/data-sources", json={
        "name": "To Delete",
        "request_url": "https://delete.example.com",
    }, headers=headers)
    source_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/data-sources/{source_id}", headers=headers)
    assert resp.status_code == 204

    # Verify deleted
    resp = await client.get(f"/api/v1/data-sources/{source_id}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient, db):
    """Users without proper roles cannot manage data sources."""
    # Register a regular user
    await client.post("/api/v1/auth/register", json={
        "username": "regular",
        "email": "regular@test.com",
        "password": "regular123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "regular",
        "password": "regular123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create data source — should be forbidden
    resp = await client.post("/api/v1/data-sources", json={
        "name": "Unauthorized",
        "request_url": "https://hack.example.com",
    }, headers=headers)
    assert resp.status_code == 403
