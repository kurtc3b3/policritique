import pytest

from policritique.collectors.members import _store_members
from policritique.db.engine import dispose_engine
from policritique.db.models import Member, MemberContact, MemberTerm
from policritique.parliament.members_api import MemberSummary
from policritique.parliament.mnis import ParsedContact
from policritique.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_store_members_persists_contacts(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    await dispose_engine()
    get_settings.cache_clear()

    from policritique.db.store import Database

    db = Database()
    await db.init()

    members = [
        MemberSummary(
            parliament_member_id=172,
            name_list_as="Abbott, Ms Diane",
            name_display_as="Ms Diane Abbott",
            name_full_title="Rt Hon Diane Abbott MP",
            gender="F",
            party_name="Independent",
            party_abbreviation="Ind",
            constituency_name="Hackney North and Stoke Newington",
            membership_start_date="1987-06-11",
            membership_end_date=None,
            is_current=True,
        )
    ]
    contacts = {
        172: [
            ParsedContact("email", "diane.abbott.office@parliament.uk", False),
            ParsedContact("phone", "020 7219 4426", False),
        ]
    }

    count = await _store_members(db, members=members, contacts_by_member_id=contacts)
    assert count == 1

    async with db._sessions() as session:
        from sqlalchemy import select

        stored_members = (await session.execute(select(Member))).scalars().all()
        terms = (await session.execute(select(MemberTerm))).scalars().all()
        member_contacts = (await session.execute(select(MemberContact))).scalars().all()

    assert len(stored_members) == 1
    assert stored_members[0].parliament_member_id == 172
    assert stored_members[0].is_current == 1
    assert len(terms) == 1
    assert terms[0].house == "Commons"
    assert len(member_contacts) == 2

    await dispose_engine()
