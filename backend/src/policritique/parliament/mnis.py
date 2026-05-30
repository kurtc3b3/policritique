"""Fetch and parse MNIS member contact data."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass

import httpx

from policritique.settings import get_settings

CURRENT_COMMONS_QUERY = "House=Commons|IsEligible=true"


@dataclass(frozen=True, slots=True)
class ParsedContact:
    contact_type: str
    value: str
    is_primary: bool


class MnisClient:
    def __init__(self, base_url: str | None = None, timeout: float = 120.0) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.parliament_data_base_url).rstrip("/")
        self.timeout = timeout

    def query_url(self, search: str, outputs: str) -> str:
        encoded_search = search.replace("|", "%7C")
        return f"{self.base_url}/services/mnis/members/query/{encoded_search}/{outputs}/"

    async def fetch_json(self, search: str, outputs: str) -> dict:
        url = self.query_url(search, outputs)
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            text = response.content.decode("utf-8-sig")
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object from {url}")
            return payload

    async def fetch_current_commons_contacts(self) -> dict[int, list[ParsedContact]]:
        payload = await self.fetch_json(CURRENT_COMMONS_QUERY, "Addresses")
        return parse_mnis_addresses_payload(payload)


def parse_mnis_addresses_payload(payload: dict) -> dict[int, list[ParsedContact]]:
    members = _member_list(payload.get("Members") or {})
    contacts_by_id: dict[int, list[ParsedContact]] = {}

    for member in members:
        member_id = _member_id(member)
        if member_id is None:
            continue
        addresses = _address_list(member.get("Addresses") or {})
        contacts = _dedupe_contacts(
            contact for address in addresses for contact in contacts_from_mnis_address(address)
        )
        if contacts:
            contacts_by_id[member_id] = contacts

    return contacts_by_id


def contacts_from_mnis_address(address: dict) -> list[ParsedContact]:
    contact_type = _contact_type_slug(address.get("Type"))
    is_primary = _parse_bool(address.get("IsPreferred"))
    contacts: list[ParsedContact] = []

    email = _optional_str(address.get("Email"))
    if email:
        contacts.append(ParsedContact("email", email, is_primary))

    phone = _optional_str(address.get("Phone"))
    if phone:
        contacts.append(ParsedContact("phone", phone, is_primary))

    website = _optional_str(address.get("Website"))
    if website:
        contacts.append(ParsedContact("website", website, is_primary))

    if _parse_bool(address.get("IsPhysical")):
        postal = _format_postal_address(address)
        if postal:
            contacts.append(ParsedContact(contact_type, postal, is_primary))
        return contacts

    line = _optional_str(address.get("Address1"))
    if line:
        contacts.append(ParsedContact(contact_type, line, is_primary))

    return contacts


def _member_list(members_payload: dict | list) -> list[dict]:
    if isinstance(members_payload, list):
        return [item for item in members_payload if isinstance(item, dict)]
    member = members_payload.get("Member")
    if isinstance(member, list):
        return [item for item in member if isinstance(item, dict)]
    if isinstance(member, dict):
        return [member]
    return []


def _address_list(addresses_payload: dict | list) -> list[dict]:
    if isinstance(addresses_payload, list):
        return [item for item in addresses_payload if isinstance(item, dict)]
    address = addresses_payload.get("Address")
    if isinstance(address, list):
        return [item for item in address if isinstance(item, dict)]
    if isinstance(address, dict):
        return [address]
    return []


def _member_id(member: dict) -> int | None:
    raw = member.get("@Member_Id") or member.get("Member_Id") or member.get("MemberId")
    if raw is None:
        return None
    return int(raw)


def _format_postal_address(address: dict) -> str | None:
    parts = [_optional_str(address.get(f"Address{index}")) for index in range(1, 6)]
    parts = [part for part in parts if part]
    postcode = _optional_str(address.get("Postcode"))
    if postcode:
        parts.append(postcode)
    if not parts:
        return None
    return ", ".join(parts)


def _contact_type_slug(value: object) -> str:
    text = _optional_str(value) or "contact"
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "contact"


def _dedupe_contacts(contacts: Iterable[ParsedContact]) -> list[ParsedContact]:
    seen: set[tuple[str, str]] = set()
    unique: list[ParsedContact] = []
    for contact in contacts:
        key = (contact.contact_type, contact.value)
        if key in seen:
            continue
        seen.add(key)
        unique.append(contact)
    return unique


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}
