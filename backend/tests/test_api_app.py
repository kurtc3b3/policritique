"""Tests for FastAPI application endpoints."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from policritique.api.app import create_app
from policritique.auth.deps import current_active_user
from policritique.auth.models import User


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def active_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_parties_requires_authentication(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/parties")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_parties_list_with_authenticated_user(app, active_user):
    async def override_user() -> User:
        return active_user

    app.dependency_overrides[current_active_user] = override_user
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/parties")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["limit"] == 50
    assert body["offset"] == 0
