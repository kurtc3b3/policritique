"""Member routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from policritique.api.queries import fetch_member, fetch_members
from policritique.api.schemas import MemberDetailOut, MemberOut, PaginatedMembers
from policritique.auth.deps import current_active_user
from policritique.auth.models import User
from policritique.db.engine import get_async_session

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=PaginatedMembers)
async def list_members(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_only: bool = Query(False),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> PaginatedMembers:
    members = await fetch_members(
        session,
        limit=limit,
        offset=offset,
        current_only=current_only,
    )
    return PaginatedMembers(
        items=[MemberOut.model_validate(member) for member in members],
        limit=limit,
        offset=offset,
        count=len(members),
    )


@router.get("/{member_id}", response_model=MemberDetailOut)
async def get_member(
    member_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
) -> MemberDetailOut:
    member = await fetch_member(session, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return MemberDetailOut.model_validate(member)
