import io

import pytest
from pypdf import PdfWriter

from policritique.collectors.manifestos import store_party_manifesto
from policritique.db.engine import dispose_engine
from policritique.db.models import Election, Manifesto, Party
from policritique.manifesto.party_pdfs import PartyManifestoSource, extract_pdf_text
from policritique.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _sample_pdf_bytes(text: str) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_extract_pdf_text_returns_none_for_blank_pdf():
    assert extract_pdf_text(_sample_pdf_bytes("ignored")) is None


@pytest.mark.asyncio
async def test_store_party_manifesto_persists_text(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    await dispose_engine()
    get_settings.cache_clear()

    from policritique.db.store import Database

    db = Database()
    await db.init()

    async with db._sessions() as session:
        session.add(
            Election(
                name="2024 United Kingdom general election",
                election_type="general",
                election_date="2024-07-04",
                parliament_period="59",
                source="test",
                collected_at="2024-01-01 00:00:00",
            )
        )
        await session.commit()

    source = PartyManifestoSource(
        party_name="Labour",
        party_short_name="Lab",
        election_date="2024-07-04",
        title="2024 Labour manifesto",
        source_url="https://example.org/labour-2024.pdf",
    )
    sample_text = "Change " * 100
    await store_party_manifesto(db, source=source, text=sample_text)

    async with db._sessions() as session:
        from sqlalchemy import select

        parties = (await session.execute(select(Party))).scalars().all()
        manifestos = (await session.execute(select(Manifesto))).scalars().all()

    assert len(parties) == 1
    assert parties[0].name == "Labour"
    assert len(manifestos) == 1
    assert manifestos[0].election_id is not None
    assert len(manifestos[0].text or "") > 500

    await dispose_engine()
