"""Tests for Phase 2: Dashboard state machine and sharing."""

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
async def test_dashboard_created_as_draft(client: AsyncClient, db):
    """New dashboards should start in draft status."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Draft Board"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_publish_dashboard(client: AsyncClient, db):
    """Publishing transitions draft → published."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Publish Me"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/publish", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


@pytest.mark.asyncio
async def test_archive_dashboard(client: AsyncClient, db):
    """Archiving transitions to archived status."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Archive Me"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/archive", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_preview_dashboard(client: AsyncClient, db):
    """Preview returns full render config with widgets."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Preview Board"}, headers=headers)
    board_id = resp.json()["id"]

    # Add a widget
    await client.post(f"/api/v1/dashboards/{board_id}/widgets", json={
        "widget_type": "bar_chart",
        "title": "Sales",
        "query_config": {"table": "raw_api_records"},
        "position_config": {"x": 0, "y": 0, "w": 6, "h": 4},
        "event_config": {"event_type": "onItemClick", "target_widgets": []},
    }, headers=headers)

    resp = await client.get(f"/api/v1/dashboards/{board_id}/preview", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Preview Board"
    assert len(data["widgets"]) == 1
    assert data["widgets"][0]["widget_type"] == "bar_chart"
    assert data["widgets"][0]["query_config"] == {"table": "raw_api_records"}
    assert data["widgets"][0]["position_config"] == {"x": 0, "y": 0, "w": 6, "h": 4}
    assert data["widgets"][0]["event_config"] == {"event_type": "onItemClick", "target_widgets": []}


@pytest.mark.asyncio
async def test_share_dashboard_with_role(client: AsyncClient, db):
    """Share a dashboard with a role."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Share Board"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/share", json={
        "shared_with_role": "viewer",
        "permission_level": "view",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["shared_with_role"] == "viewer"
    assert data["permission_level"] == "view"
    assert data["dashboard_id"] == board_id


@pytest.mark.asyncio
async def test_share_dashboard_with_user(client: AsyncClient, db):
    """Share a dashboard directly with a user (by user ID)."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Get the admin user's ID
    from app.models.user import User
    from sqlalchemy import select
    user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one()

    resp = await client.post("/api/v1/dashboards", json={"name": "User Share"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/share", json={
        "shared_with_user_id": str(user.id),
        "permission_level": "edit",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["shared_with_user_id"] == str(user.id)
    assert data["permission_level"] == "edit"


@pytest.mark.asyncio
async def test_list_shares(client: AsyncClient, db):
    """List all shares for a dashboard."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Shared Board"}, headers=headers)
    board_id = resp.json()["id"]

    await client.post(f"/api/v1/dashboards/{board_id}/share", json={
        "shared_with_role": "viewer",
        "permission_level": "view",
    }, headers=headers)

    resp = await client.get(f"/api/v1/dashboards/{board_id}/shares", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["shared_with_role"] == "viewer"


@pytest.mark.asyncio
async def test_revoke_share(client: AsyncClient, db):
    """Revoke a dashboard share."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Revoke Board"}, headers=headers)
    board_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/dashboards/{board_id}/share", json={
        "shared_with_role": "viewer",
        "permission_level": "view",
    }, headers=headers)
    share_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/dashboards/{board_id}/shares/{share_id}", headers=headers)
    assert resp.status_code == 204

    # Confirm removed
    resp = await client.get(f"/api/v1/dashboards/{board_id}/shares", headers=headers)
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_publish_archived_fails(client: AsyncClient, db):
    """Cannot publish an archived dashboard."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/dashboards", json={"name": "Archived Board"}, headers=headers)
    board_id = resp.json()["id"]

    await client.post(f"/api/v1/dashboards/{board_id}/archive", headers=headers)
    resp = await client.post(f"/api/v1/dashboards/{board_id}/publish", headers=headers)
    assert resp.status_code == 422
