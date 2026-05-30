"""Constituency routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.api.queries import fetch_constituencies, fetch_constituency
from policritique.api.schemas import ConstituencyOut, PaginatedConstituencies
from policritique.auth.deps import current_active_user
from policritique.auth.models import User
from policritique.db.engine import get_async_session

router = APIRouter(prefix="/constituencies", tags=["constituencies"])


@router.get("", response_model=PaginatedConstituencies)
async def list_constituencies(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    name: str | None = Query(None, min_length=1),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedConstituencies:
    constituencies = await fetch_constituencies(session, limit=limit, offset=offset, name=name)
    return PaginatedConstituencies(
        items=[ConstituencyOut.model_validate(row) for row in constituencies],
        limit=limit,
        offset=offset,
        count=len(constituencies),
    )


@router.get("/{constituency_id}", response_model=ConstituencyOut)
async def get_constituency(
    constituency_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> ConstituencyOut:
    constituency = await fetch_constituency(session, constituency_id)
    if constituency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constituency not found",
        )
    return ConstituencyOut.model_validate(constituency)
