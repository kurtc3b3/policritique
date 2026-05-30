"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from policritique.settings import get_settings


def database_url(path: Path | None = None) -> str:
    resolved = path or get_settings().resolved_db_path
    return f"sqlite+aiosqlite:///{resolved}"


def create_engine(path: Path | None = None) -> AsyncEngine:
    engine = create_async_engine(
        database_url(path),
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
