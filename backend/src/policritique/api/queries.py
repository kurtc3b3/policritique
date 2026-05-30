"""Read-only database queries for the HTTP API."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, selectinload

from policritique.db.models import (
    Constituency,
    Election,
    ElectionResult,
    Manifesto,
    Member,
    Party,
)


async def fetch_parties(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
) -> list[Party]:
    result = await session.execute(
        select(Party).order_by(Party.name).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def fetch_party(session: AsyncSession, party_id: int) -> Party | None:
    return await session.get(Party, party_id)


async def fetch_elections(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
) -> list[Election]:
    result = await session.execute(
        select(Election).order_by(Election.election_date.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def fetch_election(session: AsyncSession, election_id: int) -> Election | None:
    return await session.get(Election, election_id)


async def fetch_election_results(
    session: AsyncSession,
    *,
    election_id: int,
    limit: int,
    offset: int,
    constituency_id: int | None = None,
) -> list[ElectionResult]:
    query = select(ElectionResult).where(ElectionResult.election_id == election_id)
    if constituency_id is not None:
        query = query.where(ElectionResult.constituency_id == constituency_id)
    query = query.order_by(ElectionResult.votes.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def fetch_constituencies(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    name: str | None = None,
) -> list[Constituency]:
    query = select(Constituency)
    if name:
        query = query.where(Constituency.name.ilike(f"%{name}%"))
    query = query.order_by(Constituency.name).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def fetch_constituency(session: AsyncSession, constituency_id: int) -> Constituency | None:
    return await session.get(Constituency, constituency_id)


async def fetch_members(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    current_only: bool = False,
) -> list[Member]:
    query = select(Member)
    if current_only:
        query = query.where(Member.is_current == 1)
    query = query.order_by(Member.name).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def fetch_member(session: AsyncSession, member_id: int) -> Member | None:
    result = await session.execute(
        select(Member)
        .where(Member.id == member_id)
        .options(
            selectinload(Member.contacts),
            selectinload(Member.terms),
        )
    )
    return result.scalar_one_or_none()


async def fetch_manifestos(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    party_id: int | None = None,
    election_id: int | None = None,
) -> list[Manifesto]:
    query = select(Manifesto).options(defer(Manifesto.text))
    if party_id is not None:
        query = query.where(Manifesto.party_id == party_id)
    if election_id is not None:
        query = query.where(Manifesto.election_id == election_id)
    query = query.order_by(Manifesto.published_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def fetch_manifesto(session: AsyncSession, manifesto_id: int) -> Manifesto | None:
    return await session.get(Manifesto, manifesto_id)
