"""Collect manifestos from the Manifesto Project and party PDFs."""

from __future__ import annotations

from policritique.console import done, info, success, warn
from policritique.db.repository import (
    find_general_election_id,
    get_or_create_party,
    upsert_manifesto,
)
from policritique.db.store import Database
from policritique.manifesto.party_pdfs import (
    PartyManifestoSource,
    build_party_manifesto_sources,
    fetch_pdf_text,
)
from policritique.manifesto.project import (
    ManifestoProjectClient,
    ManifestoProjectDocument,
    election_year_from_yyyymm,
    published_at_from_yyyymm,
)


async def collect_manifestos(
    db: Database,
    *,
    include_project: bool = True,
    include_pdfs: bool = True,
) -> int:
    """Import UK manifesto texts from Manifesto Project and party PDF sources."""
    db.ensure_exists()
    total = 0

    if include_project:
        total += await _collect_manifesto_project(db)
    if include_pdfs:
        total += await _collect_party_pdfs(db)

    await db.log_sync(
        "manifesto",
        "uk",
        "ok",
        f"Imported {total} manifestos",
    )
    done(f"Stored {total} manifestos")
    return total


async def _collect_manifesto_project(db: Database) -> int:
    client = ManifestoProjectClient()
    try:
        client.require_api_key()
    except ValueError as exc:
        warn(str(exc))
        warn("Skipping Manifesto Project import")
        return 0

    info("Fetching UK manifestos from Manifesto Project")
    documents = await client.collect_uk_documents()
    count = await _store_manifesto_project_documents(db, documents)
    success(f"Stored {count} Manifesto Project documents")
    return count


async def _collect_party_pdfs(db: Database) -> int:
    info("Fetching official and archived party manifesto PDFs")
    sources = build_party_manifesto_sources()
    stored = 0

    for source in sources:
        try:
            text = await fetch_pdf_text(source.source_url)
        except Exception as exc:
            warn(f"Failed to fetch {source.title}: {exc}")
            continue

        if not text or len(text) < 500:
            warn(f"Skipping {source.title}: extracted text too short")
            continue

        async with db._sessions() as session:
            party_id = await get_or_create_party(
                session,
                ec_id=None,
                name=source.party_name,
                short_name=source.party_short_name,
            )
            election_id = await find_general_election_id(
                session,
                year=int(source.election_date[:4]),
            )
            await upsert_manifesto(
                session,
                party_id=party_id,
                election_id=election_id,
                title=source.title,
                source_url=source.source_url,
                published_at=source.election_date,
                text=text,
            )
            await session.commit()
        stored += 1

    success(f"Stored {stored} party PDF manifestos")
    return stored


async def _store_manifesto_project_documents(
    db: Database,
    documents: list[ManifestoProjectDocument],
) -> int:
    async with db._sessions() as session:
        for document in documents:
            party_id = await get_or_create_party(
                session,
                ec_id=None,
                name=document.party_name,
            )
            election_id = await find_general_election_id(
                session,
                year=election_year_from_yyyymm(document.date_yyyymm),
            )
            source_url = document.source_url or (f"manifesto-project://{document.manifesto_id}")
            await upsert_manifesto(
                session,
                party_id=party_id,
                election_id=election_id,
                title=document.title,
                source_url=source_url,
                published_at=published_at_from_yyyymm(document.date_yyyymm),
                text=document.text,
            )
        await session.commit()
    return len(documents)


async def store_party_manifesto(
    db: Database,
    *,
    source: PartyManifestoSource,
    text: str,
) -> None:
    async with db._sessions() as session:
        party_id = await get_or_create_party(
            session,
            ec_id=None,
            name=source.party_name,
            short_name=source.party_short_name,
        )
        election_id = await find_general_election_id(
            session,
            year=int(source.election_date[:4]),
        )
        await upsert_manifesto(
            session,
            party_id=party_id,
            election_id=election_id,
            title=source.title,
            source_url=source.source_url,
            published_at=source.election_date,
            text=text,
        )
        await session.commit()
