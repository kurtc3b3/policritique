import pytest

from policritique.collectors.elections import _store_candidacies
from policritique.db.engine import dispose_engine
from policritique.db.models import Election, ElectionResult, Party
from policritique.parliament.psephology import parse_candidacies_csv
from policritique.settings import get_settings

SAMPLE_CSV = """\
ONS ID,Constituency name,Country name,Party name,Party abbreviation,\
Electoral Commission party ID,Candidate first name,Candidate surname,Votes,Share
E14001063,Example East,England,Labour,Lab,PP53,Jane,Smith,18000,0.45
E14001063,Example East,England,Conservative,Con,PP52,John,Doe,15000,0.375
"""


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_store_candidacies_persists_results(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    await dispose_engine()
    get_settings.cache_clear()

    from policritique.db.store import Database

    db = Database()
    await db.init()

    candidacies = parse_candidacies_csv(SAMPLE_CSV)
    count = await _store_candidacies(
        db,
        parliament_id=59,
        election_date="2024-07-04",
        candidacies=candidacies,
        source="test://candidacies.csv",
    )

    assert count == 2

    async with db._sessions() as session:
        from sqlalchemy import func, select

        elections = (await session.execute(select(Election))).scalars().all()
        parties = (await session.execute(select(Party))).scalars().all()
        results = (await session.execute(select(ElectionResult))).scalars().all()
        winners = (
            await session.execute(
                select(func.count())
                .select_from(ElectionResult)
                .where(ElectionResult.is_elected == 1)
            )
        ).scalar_one()

    assert len(elections) == 1
    assert elections[0].election_date == "2024-07-04"
    assert len(parties) == 2
    assert len(results) == 2
    assert winners == 1

    await dispose_engine()
