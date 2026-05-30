"""Async SQLite persistence via SQLAlchemy."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from policritique.console import info, warn
from policritique.db.engine import get_engine, get_session_maker
from policritique.db.models import Base, SyncLog
from policritique.settings import get_settings


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or get_settings().resolved_db_path
        self._engine = get_engine()
        self._sessions = get_session_maker()

    async def close(self) -> None:
        pass

    async def init(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            warn(f"Database already exists: {self.path}")
            return self.path

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        info(f"Created database: [bold]{self.path}[/bold]")
        return self.path

    def ensure_exists(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"Database not found at {self.path}. Run: policritique init-db")

    async def log_sync(self, entity_type: str, entity_ref: str, status: str, message: str) -> None:
        async with self._sessions() as session:
            session.add(
                SyncLog(
                    entity_type=entity_type,
                    entity_ref=entity_ref,
                    status=status,
                    message=message,
                    synced_at=_now(),
                )
            )
            await session.commit()
