"""Database query and upsert helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.db.models import (
    Constituency,
    Election,
    ElectionResult,
    Manifesto,
    Member,
    MemberContact,
    MemberTerm,
    Party,
)


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


async def get_or_create_party(
    session: AsyncSession,
    *,
    ec_id: str | None,
    name: str,
    short_name: str | None = None,
) -> int:
    if ec_id:
        result = await session.execute(select(Party.id).where(Party.ec_id == ec_id))
        party_id = result.scalar_one_or_none()
        if party_id is not None:
            return party_id

    result = await session.execute(select(Party.id).where(Party.name == name))
    party_id = result.scalar_one_or_none()
    if party_id is not None:
        return party_id

    party = Party(ec_id=ec_id, name=name, short_name=short_name, collected_at=_now())
    session.add(party)
    await session.flush()
    return party.id


async def get_or_create_constituency(
    session: AsyncSession,
    *,
    name: str,
    gss_code: str | None,
    country: str | None,
) -> int:
    if gss_code:
        result = await session.execute(
            select(Constituency.id).where(Constituency.gss_code == gss_code)
        )
        constituency_id = result.scalar_one_or_none()
        if constituency_id is not None:
            return constituency_id

    result = await session.execute(select(Constituency.id).where(Constituency.name == name))
    constituency_id = result.scalar_one_or_none()
    if constituency_id is not None:
        return constituency_id

    constituency = Constituency(
        name=name,
        gss_code=gss_code or None,
        country=country or None,
        collected_at=_now(),
    )
    session.add(constituency)
    await session.flush()
    return constituency.id


async def get_or_create_election(
    session: AsyncSession,
    *,
    name: str,
    election_type: str,
    election_date: str,
    parliament_period: str | None,
    source: str | None,
) -> int:
    result = await session.execute(
        select(Election.id).where(
            Election.election_date == election_date,
            Election.election_type == election_type,
        )
    )
    election_id = result.scalar_one_or_none()
    if election_id is not None:
        return election_id

    election = Election(
        name=name,
        election_type=election_type,
        election_date=election_date,
        parliament_period=parliament_period,
        source=source,
        collected_at=_now(),
    )
    session.add(election)
    await session.flush()
    return election.id


async def upsert_election_result(
    session: AsyncSession,
    *,
    election_id: int,
    constituency_id: int,
    party_id: int | None,
    candidate_name: str,
    votes: int | None,
    vote_share: float | None,
    is_elected: bool,
) -> None:
    now = _now()
    result = await session.execute(
        select(ElectionResult).where(
            ElectionResult.election_id == election_id,
            ElectionResult.constituency_id == constituency_id,
            ElectionResult.candidate_name == candidate_name,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        session.add(
            ElectionResult(
                election_id=election_id,
                constituency_id=constituency_id,
                party_id=party_id,
                candidate_name=candidate_name,
                votes=votes,
                vote_share=vote_share,
                is_elected=int(is_elected),
                collected_at=now,
            )
        )
        return

    row.party_id = party_id
    row.votes = votes
    row.vote_share = vote_share
    row.is_elected = int(is_elected)
    row.collected_at = now


async def upsert_member(
    session: AsyncSession,
    *,
    parliament_member_id: int,
    name: str,
    display_name: str | None,
    gender: str | None,
    is_current: bool,
) -> int:
    now = _now()
    result = await session.execute(
        select(Member).where(Member.parliament_member_id == parliament_member_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        member = Member(
            parliament_member_id=parliament_member_id,
            name=name,
            display_name=display_name,
            gender=gender,
            is_current=int(is_current),
            collected_at=now,
        )
        session.add(member)
        await session.flush()
        return member.id

    member.name = name
    member.display_name = display_name
    member.gender = gender
    member.is_current = int(is_current)
    member.collected_at = now
    return member.id


async def upsert_member_term(
    session: AsyncSession,
    *,
    member_id: int,
    constituency_id: int | None,
    party_id: int | None,
    house: str,
    start_date: str | None,
    end_date: str | None,
) -> None:
    now = _now()
    result = await session.execute(
        select(MemberTerm).where(
            MemberTerm.member_id == member_id,
            MemberTerm.house == house,
            MemberTerm.start_date == start_date,
        )
    )
    term = result.scalar_one_or_none()
    if term is None:
        session.add(
            MemberTerm(
                member_id=member_id,
                constituency_id=constituency_id,
                party_id=party_id,
                house=house,
                start_date=start_date,
                end_date=end_date,
                collected_at=now,
            )
        )
        return

    term.constituency_id = constituency_id
    term.party_id = party_id
    term.end_date = end_date
    term.collected_at = now


async def replace_member_contacts(
    session: AsyncSession,
    *,
    member_id: int,
    contacts: list[tuple[str, str, bool]],
) -> None:
    now = _now()
    await session.execute(delete(MemberContact).where(MemberContact.member_id == member_id))
    for contact_type, value, is_primary in contacts:
        session.add(
            MemberContact(
                member_id=member_id,
                contact_type=contact_type,
                value=value,
                is_primary=int(is_primary),
                collected_at=now,
            )
        )


async def find_general_election_id(session: AsyncSession, *, year: int) -> int | None:
    result = await session.execute(
        select(Election.id)
        .where(
            Election.election_type == "general",
            Election.election_date.like(f"{year}-%"),
        )
        .order_by(Election.election_date.desc())
    )
    return result.scalars().first()


async def upsert_manifesto(
    session: AsyncSession,
    *,
    party_id: int,
    election_id: int | None,
    title: str,
    source_url: str | None,
    published_at: str | None,
    text: str | None,
) -> None:
    now = _now()
    if source_url:
        result = await session.execute(select(Manifesto).where(Manifesto.source_url == source_url))
    else:
        result = await session.execute(
            select(Manifesto).where(Manifesto.party_id == party_id, Manifesto.title == title)
        )
    manifesto = result.scalar_one_or_none()
    if manifesto is None:
        session.add(
            Manifesto(
                party_id=party_id,
                election_id=election_id,
                title=title,
                source_url=source_url,
                published_at=published_at,
                text=text,
                collected_at=now,
            )
        )
        return

    manifesto.party_id = party_id
    manifesto.election_id = election_id
    manifesto.title = title
    manifesto.published_at = published_at
    manifesto.text = text
    manifesto.collected_at = now
