"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from policritique.api.routers import constituencies, elections, manifestos, members, parties
from policritique.auth.deps import auth_backend, fastapi_users
from policritique.auth.models import User  # noqa: F401 — register user table
from policritique.auth.schemas import UserCreate, UserRead, UserUpdate
from policritique.db.engine import dispose_engine, get_engine
from policritique.db.models import Base
from policritique.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="policritique API",
        description="Query UK political open data — elections, MPs, and manifestos.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
    app.include_router(parties.router)
    app.include_router(elections.router)
    app.include_router(constituencies.router)
    app.include_router(members.router)
    app.include_router(manifestos.router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
