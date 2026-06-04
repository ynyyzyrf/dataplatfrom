"""Tests for data record browsing API."""

import pytest
from httpx import AsyncClient

from app.services.role_service import seed_default_roles


async def _get_admin_token(client: AsyncClient, db) -> str:
    await seed_default_roles(db)
    await db.commit()
    resp = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_records_empty(client: AsyncClient, db):
    """List data records when none exist."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/data-records", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_records_requires_auth(client: AsyncClient):
    """Data records endpoint requires authentication."""
    resp = await client.get("/api/v1/data-records")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_record_not_found(client: AsyncClient, db):
    """Getting a non-existent record returns 404."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/data-records/nonexistent-id", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_records_with_filters(client: AsyncClient, db):
    """List data records with data_source_id filter."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # First create a data source
    ds_resp = await client.post("/api/v1/data-sources", json={
        "name": "Test DS for Records",
        "request_method": "GET",
        "request_url": "https://example.com/api",
        "auth_type": "none",
    }, headers=headers)
    assert ds_resp.status_code == 200
    ds_id = ds_resp.json()["id"]

    # List records filtered by this data source (should be empty)
    resp = await client.get(f"/api/v1/data-records?data_source_id={ds_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_records_pagination(client: AsyncClient, db):
    """Test pagination parameters work correctly."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/data-records?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
