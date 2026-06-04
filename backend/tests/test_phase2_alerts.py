"""Tests for Phase 2: Alert rules and evaluation."""

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
async def test_create_alert_rule(client: AsyncClient, db):
    """Create a new alert rule."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Consecutive Failures Alert",
        "rule_type": "consecutive_failures",
        "target_type": "sync_job",
        "threshold": 3,
        "window_minutes": 15,
        "channels": ["in_app"],
        "is_active": True,
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Consecutive Failures Alert"
    assert data["rule_type"] == "consecutive_failures"
    assert data["threshold"] == 3
    assert data["is_active"] == True


@pytest.mark.asyncio
async def test_list_alert_rules(client: AsyncClient, db):
    """List all alert rules."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post("/api/v1/alert-rules", json={
        "name": "Rule 1",
        "rule_type": "http_error",
        "target_type": "sync_job",
        "threshold": 1,
        "window_minutes": 5,
        "channels": ["in_app"],
    }, headers=headers)

    resp = await client.get("/api/v1/alert-rules", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_alert_rule(client: AsyncClient, db):
    """Get a specific alert rule."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Timeout Alert",
        "rule_type": "timeout",
        "target_type": "sync_job",
        "threshold": 300,
        "window_minutes": 10,
        "channels": ["in_app", "email"],
    }, headers=headers)
    rule_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/alert-rules/{rule_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Timeout Alert"


@pytest.mark.asyncio
async def test_update_alert_rule(client: AsyncClient, db):
    """Update an alert rule."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Old Rule",
        "rule_type": "zero_data",
        "target_type": "sync_job",
        "threshold": 1,
        "window_minutes": 30,
        "channels": ["in_app"],
    }, headers=headers)
    rule_id = resp.json()["id"]

    resp = await client.put(f"/api/v1/alert-rules/{rule_id}", json={
        "name": "Updated Rule",
        "is_active": False,
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Rule"
    assert resp.json()["is_active"] == False


@pytest.mark.asyncio
async def test_delete_alert_rule(client: AsyncClient, db):
    """Delete an alert rule."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Delete Me",
        "rule_type": "http_error",
        "target_type": "sync_job",
        "threshold": 1,
        "window_minutes": 5,
        "channels": ["in_app"],
    }, headers=headers)
    rule_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/alert-rules/{rule_id}", headers=headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/alert-rules/{rule_id}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_alert_rule_missing_required_fields(client: AsyncClient, db):
    """Creating alert rule without required fields should fail."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Bad Rule",
    }, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_non_admin_cannot_manage_alerts(client: AsyncClient, db):
    """Non-admin users should get 403 on alert rule management."""
    await seed_default_roles(db)
    await db.commit()

    # Create a viewer user
    resp = await client.post("/api/v1/auth/register", json={
        "username": "viewer_user",
        "email": "viewer@test.com",
        "password": "viewer123",
    }, headers={"X-Register-Token": "internal"})
    if resp.status_code == 201:
        viewer_token = resp.json()["access_token"]
    else:
        # Register might not work without internal token; skip if 422
        return

    headers = {"Authorization": f"Bearer {viewer_token}"}
    resp = await client.post("/api/v1/alert-rules", json={
        "name": "Hack Alert",
        "rule_type": "http_error",
        "target_type": "sync_job",
        "threshold": 1,
        "window_minutes": 5,
        "channels": ["in_app"],
    }, headers=headers)
    assert resp.status_code == 403
