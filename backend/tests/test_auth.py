"""Auth API integration tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    payload = {"username": "testuser", "email": "test@example.com", "password": "testpass123"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # First register
    await client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "testpass123"
    })
    # Then login
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "testpass123"
    })
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser", "password": "wrongpassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "testpass123"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser", "password": "testpass123"
    })
    token = login_resp.json()["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"
