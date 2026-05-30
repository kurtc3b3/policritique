"""Fetch and parse UK Parliament Members API data."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from policritique.settings import get_settings

COMMONS_HOUSE = 1


@dataclass(frozen=True, slots=True)
class MemberSummary:
    parliament_member_id: int
    name_list_as: str
    name_display_as: str
    name_full_title: str
    gender: str | None
    party_name: str | None
    party_abbreviation: str | None
    constituency_name: str | None
    membership_start_date: str | None
    membership_end_date: str | None
    is_current: bool


class MembersApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 60.0) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.members_api_base_url).rstrip("/")
        self.timeout = timeout

    async def fetch_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | bool] | None = None,
    ) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object from {url}")
            return payload

    async def search_commons_members(self, *, is_current: bool = True) -> list[MemberSummary]:
        members: list[MemberSummary] = []
        skip = 0
        take = 100

        while True:
            payload = await self.fetch_json(
                "/api/Members/Search",
                params={
                    "House": "Commons",
                    "IsCurrentMember": is_current,
                    "skip": skip,
                    "take": take,
                },
            )
            items = payload.get("items") or []
            for item in items:
                parsed = parse_member_summary(item.get("value") or {})
                if parsed is not None:
                    members.append(parsed)

            total = int(payload.get("totalResults") or 0)
            skip += len(items)
            if skip >= total or not items:
                break

        return members


def parse_member_summary(value: dict) -> MemberSummary | None:
    member_id = value.get("id")
    if member_id is None:
        return None

    party = value.get("latestParty") or {}
    membership = value.get("latestHouseMembership") or {}
    status = membership.get("membershipStatus") or {}

    return MemberSummary(
        parliament_member_id=int(member_id),
        name_list_as=str(value.get("nameListAs") or ""),
        name_display_as=str(value.get("nameDisplayAs") or ""),
        name_full_title=str(value.get("nameFullTitle") or ""),
        gender=_optional_str(value.get("gender")),
        party_name=_optional_str(party.get("name")),
        party_abbreviation=_optional_str(party.get("abbreviation")),
        constituency_name=_optional_str(membership.get("membershipFrom")),
        membership_start_date=_parse_api_date(membership.get("membershipStartDate")),
        membership_end_date=_parse_api_date(membership.get("membershipEndDate")),
        is_current=bool(status.get("statusIsActive")),
    )


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_api_date(value: object) -> str | None:
    text = _optional_str(value)
    if not text:
        return None
    return text[:10]
