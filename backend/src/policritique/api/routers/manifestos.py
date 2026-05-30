"""Manifesto routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.api.queries import fetch_manifesto, fetch_manifestos
from policritique.api.schemas import ManifestoDetailOut, ManifestoOut, PaginatedManifestos
from policritique.auth.deps import current_active_user
from policritique.auth.models import User
from policritique.db.engine import get_async_session

router = APIRouter(prefix="/manifestos", tags=["manifestos"])


@router.get("", response_model=PaginatedManifestos)
async def list_manifestos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    party_id: int | None = Query(None),
    election_id: int | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedManifestos:
    manifestos = await fetch_manifestos(
        session,
        limit=limit,
        offset=offset,
        party_id=party_id,
        election_id=election_id,
    )
    return PaginatedManifestos(
        items=[ManifestoOut.model_validate(row) for row in manifestos],
        limit=limit,
        offset=offset,
        count=len(manifestos),
    )


@router.get("/{manifesto_id}", response_model=ManifestoDetailOut)
async def get_manifesto(
    manifesto_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> ManifestoDetailOut:
    manifesto = await fetch_manifesto(session, manifesto_id)
    if manifesto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manifesto not found")
    return ManifestoDetailOut.model_validate(manifesto)
