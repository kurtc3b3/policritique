"""Party routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.api.queries import fetch_parties, fetch_party
from policritique.api.schemas import PaginatedParties, PartyOut
from policritique.auth.deps import current_active_user
from policritique.auth.models import User
from policritique.db.engine import get_async_session

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("", response_model=PaginatedParties)
async def list_parties(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedParties:
    parties = await fetch_parties(session, limit=limit, offset=offset)
    return PaginatedParties(
        items=[PartyOut.model_validate(party) for party in parties],
        limit=limit,
        offset=offset,
        count=len(parties),
    )


@router.get("/{party_id}", response_model=PartyOut)
async def get_party(
    party_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PartyOut:
    party = await fetch_party(session, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
    return PartyOut.model_validate(party)
