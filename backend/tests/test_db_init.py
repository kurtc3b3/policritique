import pytest
from sqlalchemy import inspect

from policritique.db.engine import get_engine
from policritique.db.models import Base
from policritique.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_init_db_creates_all_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    from policritique.db.engine import dispose_engine
    from policritique.db.store import Database

    await dispose_engine()
    get_settings.cache_clear()

    db = Database()
    await db.init()

    async with get_engine().connect() as conn:
        table_names = await conn.run_sync(
            lambda sync_conn: set(inspect(sync_conn).get_table_names())
        )

    expected = {table.name for table in Base.metadata.sorted_tables}
    assert expected.issubset(table_names)

    await dispose_engine()
