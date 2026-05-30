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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
)
async def test_cors_allows_vite_origins(app, origin: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health", headers={"Origin": origin})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


@pytest.mark.asyncio
async def test_cors_preflight_allows_authorization_header(app):
    origin = "http://localhost:5173"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/parties",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert "authorization" in (response.headers.get("access-control-allow-headers") or "").lower()
