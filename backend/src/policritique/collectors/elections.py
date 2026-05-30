"""Collect general election results from UK Parliament psephology data."""

from __future__ import annotations

from policritique.console import done, info, success
from policritique.db.repository import (
    get_or_create_constituency,
    get_or_create_election,
    get_or_create_party,
    upsert_election_result,
)
from policritique.db.store import Database
from policritique.parliament.psephology import (
    DEFAULT_PARLIAMENTS,
    CandidacyRow,
    PsephologyClient,
    candidate_full_name,
    winning_candidate_keys,
)


async def collect_general_elections(
    db: Database,
    *,
    parliament_ids: list[int] | None = None,
) -> int:
    """Import candidacy-level results for one or more parliamentary periods."""
    db.ensure_exists()
    client = PsephologyClient()
    parliament_dates = await client.load_parliament_election_dates()
    targets = parliament_ids or list(DEFAULT_PARLIAMENTS)

    total_results = 0
    for parliament_id in targets:
        election_date = parliament_dates.get(parliament_id)
        if not election_date:
            raise ValueError(f"No election date found for parliament period {parliament_id}")

        info(
            f"Collecting general election results for parliament {parliament_id} ({election_date})"
        )
        candidacies = await client.fetch_candidacies(parliament_id)
        count = await _store_candidacies(
            db,
            parliament_id=parliament_id,
            election_date=election_date,
            candidacies=candidacies,
            source=client.candidacies_url(parliament_id),
        )
        total_results += count
        success(f"Stored {count} candidacies for {election_date}")
        await db.log_sync(
            "election",
            f"parliament:{parliament_id}",
            "ok",
            f"Imported {count} candidacies for {election_date}",
        )

    done(f"Stored {total_results} election results across {len(targets)} elections")
    return total_results


async def _store_candidacies(
    db: Database,
    *,
    parliament_id: int,
    election_date: str,
    candidacies: list[CandidacyRow],
    source: str,
) -> int:
    winners = winning_candidate_keys(candidacies)
    election_name = f"{election_date} United Kingdom general election"

    async with db._sessions() as session:
        election_id = await get_or_create_election(
            session,
            name=election_name,
            election_type="general",
            election_date=election_date,
            parliament_period=str(parliament_id),
            source=source,
        )

        for row in candidacies:
            candidate_name = candidate_full_name(row.candidate_first_name, row.candidate_surname)
            party_id = await get_or_create_party(
                session,
                ec_id=row.ec_party_id,
                name=row.party_name,
                short_name=row.party_abbreviation,
            )
            constituency_id = await get_or_create_constituency(
                session,
                name=row.constituency_name,
                gss_code=row.ons_id or None,
                country=row.country_name or None,
            )
            is_elected = (row.ons_id, row.constituency_name, candidate_name) in winners
            await upsert_election_result(
                session,
                election_id=election_id,
                constituency_id=constituency_id,
                party_id=party_id,
                candidate_name=candidate_name,
                votes=row.votes,
                vote_share=row.vote_share,
                is_elected=is_elected,
            )

        await session.commit()
    return len(candidacies)
