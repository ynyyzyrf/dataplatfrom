"""Tests for sync job management API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.role_service import seed_default_roles
from app.models.data_source import DataSource


async def _get_admin_token(client: AsyncClient, db) -> str:
    await seed_default_roles(db)
    await db.commit()
    resp = await client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "admin123",
    })
    return resp.json()["access_token"]


async def _create_data_source(client: AsyncClient, headers: dict, name: str = "Test DS") -> str:
    resp = await client.post("/api/v1/data-sources", json={
        "name": name,
        "request_url": "https://jsonplaceholder.typicode.com/posts",
    }, headers=headers)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_sync_jobs_empty(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/sync-jobs", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_create_sync_job(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    ds_id = await _create_data_source(client, headers)

    resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": ds_id,
        "name": "Hourly Sync",
        "schedule_type": "interval",
        "schedule_config": {"interval_minutes": 60},
        "is_enabled": True,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Hourly Sync"
    assert data["is_enabled"] is True


@pytest.mark.asyncio
async def test_create_sync_job_invalid_ds(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": "nonexistent",
        "name": "Bad Job",
    }, headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_sync_job(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    ds_id = await _create_data_source(client, headers)

    resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": ds_id,
        "name": "Old Job Name",
    }, headers=headers)
    job_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/sync-jobs/{job_id}", json={
        "name": "New Job Name",
        "is_enabled": False,
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Job Name"
    assert data["is_enabled"] is False


@pytest.mark.asyncio
async def test_delete_sync_job(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    ds_id = await _create_data_source(client, headers)

    resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": ds_id,
        "name": "To Be Deleted",
    }, headers=headers)
    job_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/sync-jobs/{job_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_execute_sync_job(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    ds_id = await _create_data_source(client, headers)

    resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": ds_id,
        "name": "Manual Sync",
    }, headers=headers)
    job_id = resp.json()["id"]

    # Execute the sync
    resp = await client.post(f"/api/v1/sync-jobs/{job_id}/execute", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("completed", "failed")
    assert data["sync_job_id"] == job_id
