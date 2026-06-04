"""Tests for Phase 2: Notification service."""

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
async def test_list_notifications_empty(client: AsyncClient, db):
    """List notifications initially empty."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_unread_count_zero(client: AsyncClient, db):
    """Unread count is zero when no notifications."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_notifications_triggered_on_failed_job(client: AsyncClient, db):
    """When a sync job fails with an active alert rule, notifications should be created."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create data source (use a bad URL to trigger failure)
    ds_resp = await client.post("/api/v1/data-sources", json={
        "name": "Bad API Source",
        "source_type": "rest_api",
        "request_url": "https://invalid.example.com/api",
        "request_method": "GET",
        "auth_type": "none",
        "timeout_seconds": 2,
    }, headers=headers)
    if ds_resp.status_code != 201:
        pytest.skip("Could not create data source")
    ds_id = ds_resp.json()["id"]

    # Create sync job
    job_resp = await client.post("/api/v1/sync-jobs", json={
        "data_source_id": ds_id,
        "name": "Test Alert Job",
        "schedule_type": "interval",
        "schedule_config": {"interval_minutes": 60},
    }, headers=headers)
    job_id = job_resp.json()["id"]

    # Create alert rule for this job
    await client.post("/api/v1/alert-rules", json={
        "name": "HTTP Error Alert",
        "rule_type": "http_error",
        "target_type": "sync_job",
        "target_id": job_id,
        "threshold": 1,
        "window_minutes": 5,
        "channels": ["in_app"],
    }, headers=headers)

    # Execute sync job (will fail due to bad URL)
    resp = await client.post(f"/api/v1/sync-jobs/{job_id}/execute", headers=headers)
    # The job execution should still succeed (even with error response)
    # because execute_job catches the error and marks as failed

    # Check notifications were created
    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # Notifications should have been created for admin users
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_mark_notification_read(client: AsyncClient, db):
    """Mark a notification as read."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Create notification via service directly
    from app.services.notification_service import NotificationService
    from app.models.user import User
    from sqlalchemy import select

    user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one()
    svc = NotificationService()
    notif = await svc.create_notification(
        db, str(user.id),
        title="Test", message="Test notification",
        notification_type="info",
    )
    await db.commit()

    resp = await client.patch(f"/api/v1/notifications/{notif.id}/read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_read"] == True


@pytest.mark.asyncio
async def test_mark_all_read(client: AsyncClient, db):
    """Mark all notifications as read."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    from app.services.notification_service import NotificationService
    from app.models.user import User
    from sqlalchemy import select

    user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one()
    svc = NotificationService()
    await svc.create_notification(db, str(user.id), title="N1", message="Msg 1")
    await svc.create_notification(db, str(user.id), title="N2", message="Msg 2")
    await db.commit()

    resp = await client.patch("/api/v1/notifications/mark-all-read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["marked_read"] >= 2

    resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert resp.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_unread_only_filter(client: AsyncClient, db):
    """Filter notifications to unread only."""
    token = await _get_admin_token(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    from app.services.notification_service import NotificationService
    from app.models.user import User
    from sqlalchemy import select

    user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one()
    svc = NotificationService()
    n1 = await svc.create_notification(db, str(user.id), title="Unread", message="Msg unread")
    n2 = await svc.create_notification(db, str(user.id), title="Read", message="Msg read")
    await svc.mark_read(db, str(n2.id), str(user.id))
    await db.commit()

    resp = await client.get("/api/v1/notifications?unread_only=true", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Unread"
