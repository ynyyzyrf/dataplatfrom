"""Tests for dashboard and widget API."""

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
async def test_list_dashboards_empty(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/dashboards", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_create_dashboard(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={
        "name": "Sales Dashboard",
        "description": "Quarterly sales data",
        "visibility": "private",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Sales Dashboard"
    assert data["visibility"] == "private"
    assert data["widget_count"] == 0


@pytest.mark.asyncio
async def test_get_dashboard(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={
        "name": "Test Board",
    }, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/dashboards/{board_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Board"


@pytest.mark.asyncio
async def test_update_dashboard(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Old Name"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/dashboards/{board_id}", json={
        "name": "New Name",
        "status": "published",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_dashboard(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "To Delete"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/dashboards/{board_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_add_widget(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Widget Board"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/widgets", json={
        "widget_type": "bar_chart",
        "title": "Sales by Month",
        "query_config": {"table": "raw_api_records", "dimensions": ["status"], "metrics": [{"field": "id", "aggregation": "count"}]},
        "position_config": {"x": 0, "y": 0, "w": 6, "h": 4},
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["widget_type"] == "bar_chart"
    assert data["title"] == "Sales by Month"
    assert data["dashboard_id"] == board_id


@pytest.mark.asyncio
async def test_delete_widget(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "W Board"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/widgets", json={
        "widget_type": "table", "title": "Data Table",
    }, headers=headers)
    widget_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/dashboards/widgets/{widget_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_query_endpoint(client: AsyncClient, db):
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards/query", json={
        "table": "raw_api_records",
        "dimensions": ["response_status"],
        "metrics": [{"field": "id", "aggregation": "count", "alias": "total"}],
    }, headers=headers)

    # Should return even with empty data
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data
    assert "rows" in data
    assert "total" in data
