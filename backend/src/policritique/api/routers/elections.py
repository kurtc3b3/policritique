"""Election routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.api.queries import fetch_election, fetch_election_results, fetch_elections
from policritique.api.schemas import (
    ElectionOut,
    ElectionResultOut,
    PaginatedElectionResults,
    PaginatedElections,
)
from policritique.auth.deps import current_active_user
from policritique.auth.models import User
from policritique.db.engine import get_async_session

router = APIRouter(prefix="/elections", tags=["elections"])


@router.get("", response_model=PaginatedElections)
async def list_elections(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedElections:
    elections = await fetch_elections(session, limit=limit, offset=offset)
    return PaginatedElections(
        items=[ElectionOut.model_validate(election) for election in elections],
        limit=limit,
        offset=offset,
        count=len(elections),
    )


@router.get("/{election_id}", response_model=ElectionOut)
async def get_election(
    election_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> ElectionOut:
    election = await fetch_election(session, election_id)
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")
    return ElectionOut.model_validate(election)


@router.get("/{election_id}/results", response_model=PaginatedElectionResults)
async def list_election_results(
    election_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    constituency_id: int | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedElectionResults:
    election = await fetch_election(session, election_id)
    if election is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Election not found")

    results = await fetch_election_results(
        session,
        election_id=election_id,
        limit=limit,
        offset=offset,
        constituency_id=constituency_id,
    )
    return PaginatedElectionResults(
        items=[ElectionResultOut.model_validate(result) for result in results],
        limit=limit,
        offset=offset,
        count=len(results),
    )
