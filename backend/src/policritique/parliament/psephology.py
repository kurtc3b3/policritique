"""Fetch and parse UK Parliament psephology CSV data."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime

import httpx

from policritique.settings import get_settings

DEFAULT_PARLIAMENTS = (55, 56, 57, 58, 59)


@dataclass(frozen=True, slots=True)
class CandidacyRow:
    ons_id: str
    constituency_name: str
    country_name: str
    party_name: str
    party_abbreviation: str | None
    ec_party_id: str | None
    candidate_first_name: str
    candidate_surname: str
    votes: int | None
    vote_share: float | None


class PsephologyClient:
    def __init__(self, base_url: str | None = None, timeout: float = 60.0) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.psephology_base_url).rstrip("/")
        self.timeout = timeout

    async def fetch_text(self, path: str) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def load_parliament_election_dates(self) -> dict[int, str]:
        text = await self.fetch_text("parliament_periods.csv")
        dates: dict[int, str] = {}
        for row in csv.reader(io.StringIO(text)):
            if not row or not row[0].isdigit():
                continue
            parliament_id = int(row[0])
            election_date = _parse_uk_date(row[1])
            if election_date:
                dates[parliament_id] = election_date
        return dates

    async def fetch_candidacies(self, parliament_id: int) -> list[CandidacyRow]:
        path = f"results-by-parliament/{parliament_id}/general-election/candidacies.csv"
        text = await self.fetch_text(path)
        return parse_candidacies_csv(text)

    def candidacies_url(self, parliament_id: int) -> str:
        path = f"results-by-parliament/{parliament_id}/general-election/candidacies.csv"
        return f"{self.base_url}/{path}"


def _candidacies_has_header(first_row: list[str]) -> bool:
    if not first_row:
        return False
    joined = ",".join(first_row).lower()
    return "constituency name" in joined or first_row[0].strip().lower() == "ons id"


def _candidacy_from_fields(fields: list[str]) -> CandidacyRow | None:
    if len(fields) < 20:
        return None
    constituency = fields[2].strip()
    if not constituency:
        return None
    return CandidacyRow(
        ons_id=fields[0].strip(),
        constituency_name=constituency,
        country_name=fields[5].strip(),
        party_name=fields[7].strip() or "Unknown",
        party_abbreviation=_optional(fields[8]),
        ec_party_id=_optional(fields[9]),
        candidate_first_name=fields[12].strip(),
        candidate_surname=fields[13].strip(),
        votes=_parse_int(fields[18]),
        vote_share=_parse_float(fields[19]),
    )


def _candidacy_from_mapping(row: dict[str, str | None]) -> CandidacyRow | None:
    constituency = (row.get("Constituency name") or "").strip()
    if not constituency:
        return None
    return CandidacyRow(
        ons_id=(row.get("ONS ID") or "").strip(),
        constituency_name=constituency,
        country_name=(row.get("Country name") or "").strip(),
        party_name=(row.get("Party name") or "Unknown").strip(),
        party_abbreviation=_optional(row.get("Party abbreviation")),
        ec_party_id=_optional(row.get("Electoral Commission party ID")),
        candidate_first_name=(row.get("Candidate first name") or "").strip(),
        candidate_surname=(row.get("Candidate surname") or "").strip(),
        votes=_parse_int(row.get("Votes")),
        vote_share=_parse_float(row.get("Share")),
    )


def parse_candidacies_csv(text: str) -> list[CandidacyRow]:
    raw_rows = list(csv.reader(io.StringIO(text)))
    if not raw_rows:
        return []

    rows: list[CandidacyRow] = []
    if _candidacies_has_header(raw_rows[0]):
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            parsed = _candidacy_from_mapping(row)
            if parsed is not None:
                rows.append(parsed)
        return rows

    for fields in raw_rows:
        parsed = _candidacy_from_fields(fields)
        if parsed is not None:
            rows.append(parsed)
    return rows


def candidate_full_name(first_name: str, surname: str) -> str:
    return f"{first_name} {surname}".strip()


def winning_candidate_keys(rows: list[CandidacyRow]) -> set[tuple[str, str, str]]:
    """Return (ons_id, constituency_name, candidate_name) for winners by highest votes."""
    grouped: dict[tuple[str, str], list[CandidacyRow]] = {}
    for row in rows:
        key = (row.ons_id, row.constituency_name)
        grouped.setdefault(key, []).append(row)

    winners: set[tuple[str, str, str]] = set()
    for (ons_id, constituency_name), candidates in grouped.items():
        scored = [c for c in candidates if c.votes is not None]
        if not scored:
            continue
        winner = max(scored, key=lambda c: c.votes or 0)
        winners.add(
            (
                ons_id,
                constituency_name,
                candidate_full_name(winner.candidate_first_name, winner.candidate_surname),
            )
        )
    return winners


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_int(value: str | None) -> int | None:
    if value is None or not value.strip():
        return None
    return int(float(value))


def _parse_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    return float(value)


def _parse_uk_date(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None
