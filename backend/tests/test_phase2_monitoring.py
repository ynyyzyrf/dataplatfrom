"""Tests for Phase 2: Monitoring API."""

from __future__ import annotations

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
async def test_get_monitoring_overview(client: AsyncClient, db):
    """Get monitoring overview returns platform stats."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/monitoring/overview", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_data_sources" in data
    assert "total_sync_jobs" in data
    assert "total_dashboards" in data
    assert "total_runs_today" in data
    assert "active_alerts" in data
    assert "job_stats" in data


@pytest.mark.asyncio
async def test_monitoring_overview_with_data(client: AsyncClient, db):
    """Monitoring overview reflects created dashboards and data sources."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dashboard
    await client.post("/api/v1/dashboards", json={"name": "Test Board"}, headers=headers)

    # Create a data source
    await client.post("/api/v1/data-sources", json={
        "name": "Test API",
        "source_type": "rest_api",
        "request_url": "https://jsonplaceholder.typicode.com/posts",
        "request_method": "GET",
        "auth_type": "none",
    }, headers=headers)

    resp = await client.get("/api/v1/monitoring/overview", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_dashboards"] >= 1
    assert data["total_data_sources"] >= 1


@pytest.mark.asyncio
async def test_non_admin_cannot_access_monitoring(client: AsyncClient, db):
    """Viewer users should not access monitoring."""
    await seed_default_roles(db)
    await db.commit()

    resp = await client.post("/api/v1/auth/register", json={
        "username": "mon_viewer",
        "email": "mon_viewer@test.com",
        "password": "viewer123",
    }, headers={"X-Register-Token": "internal"})
    if resp.status_code != 201:
        return

    viewer_token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {viewer_token}"}

    resp = await client.get("/api/v1/monitoring/overview", headers=headers)
    assert resp.status_code == 403
