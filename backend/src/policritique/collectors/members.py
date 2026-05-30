"""Collect current MPs from the Members API and contacts from MNIS."""

from __future__ import annotations

from policritique.console import done, info, success
from policritique.db.repository import (
    get_or_create_constituency,
    get_or_create_party,
    replace_member_contacts,
    upsert_member,
    upsert_member_term,
)
from policritique.db.store import Database
from policritique.parliament.members_api import MembersApiClient, MemberSummary
from policritique.parliament.mnis import MnisClient, ParsedContact


async def collect_members(
    db: Database,
    *,
    current_only: bool = True,
) -> int:
    """Import Commons members and MNIS contact details."""
    db.ensure_exists()
    members_client = MembersApiClient()
    mnis_client = MnisClient()

    scope = "current" if current_only else "all"
    info(f"Fetching {scope} Commons members from Members API")
    members = await members_client.search_commons_members(is_current=current_only)

    info("Fetching MNIS contact addresses for eligible Commons members")
    contacts_by_member_id = await mnis_client.fetch_current_commons_contacts()

    stored = await _store_members(db, members=members, contacts_by_member_id=contacts_by_member_id)

    await db.log_sync(
        "member",
        f"commons:{scope}",
        "ok",
        f"Imported {stored} members with MNIS contacts",
    )
    done(f"Stored {stored} members ({len(contacts_by_member_id)} with contact records)")
    return stored


async def _store_members(
    db: Database,
    *,
    members: list[MemberSummary],
    contacts_by_member_id: dict[int, list[ParsedContact]],
) -> int:
    async with db._sessions() as session:
        for member in members:
            member_id = await upsert_member(
                session,
                parliament_member_id=member.parliament_member_id,
                name=member.name_list_as or member.name_display_as,
                display_name=member.name_display_as or member.name_full_title,
                gender=member.gender,
                is_current=member.is_current,
            )

            party_id = None
            if member.party_name:
                party_id = await get_or_create_party(
                    session,
                    ec_id=None,
                    name=member.party_name,
                    short_name=member.party_abbreviation,
                )

            constituency_id = None
            if member.constituency_name:
                constituency_id = await get_or_create_constituency(
                    session,
                    name=member.constituency_name,
                    gss_code=None,
                    country=None,
                )

            await upsert_member_term(
                session,
                member_id=member_id,
                constituency_id=constituency_id,
                party_id=party_id,
                house="Commons",
                start_date=member.membership_start_date,
                end_date=member.membership_end_date,
            )

            contacts = contacts_by_member_id.get(member.parliament_member_id, [])
            await replace_member_contacts(
                session,
                member_id=member_id,
                contacts=[
                    (contact.contact_type, contact.value, contact.is_primary)
                    for contact in contacts
                ],
            )

        await session.commit()

    success(f"Stored {len(members)} members")
    return len(members)
