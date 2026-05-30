"""Official and archived UK party manifesto PDF sources."""

from __future__ import annotations

import io
from dataclasses import dataclass

import httpx
from pypdf import PdfReader

ARCHIVE_BASE_URL = "https://www.politicsresources.net/area/uk/man"

ELECTION_DATES = {
    2010: "2010-05-06",
    2015: "2015-05-07",
    2017: "2017-06-08",
    2019: "2019-12-12",
    2024: "2024-07-04",
}

PARTY_CATALOG = {
    "lab": ("Labour", "Lab"),
    "cons": ("Conservative", "Con"),
    "ld": ("Liberal Democrats", "LD"),
    "green": ("Green Party", "Green"),
    "snp": ("Scottish National Party", "SNP"),
}

ELECTION_PARTY_CODES: dict[int, tuple[str, ...]] = {
    2010: ("lab", "cons", "ld", "green", "snp", "ukip"),
    2015: ("lab", "cons", "ld", "green", "snp", "ukip"),
    2017: ("lab", "cons", "ld", "green", "snp", "ukip"),
    2019: ("lab", "cons", "ld", "green", "snp", "brexit"),
    2024: ("lab", "cons", "ld", "green", "snp", "reform"),
}

EXTRA_PARTY_NAMES = {
    "ukip": ("UK Independence Party", "UKIP"),
    "brexit": ("Brexit Party", "BP"),
    "reform": ("Reform UK", "Ref"),
}

OFFICIAL_PDF_URLS: dict[tuple[str, str], str] = {
    ("2024-07-04", "Labour"): (
        "https://labour.org.uk/wp-content/uploads/2024/06/Labour-Party-manifesto-2024.pdf"
    ),
    ("2024-07-04", "Conservative"): (
        "https://public.conservatives.com/static/documents/GE2024/Conservative-Manifesto-GE2024.pdf"
    ),
    ("2024-07-04", "Liberal Democrats"): (
        "https://www.libdems.org.uk/fileadmin/groups/2_Federal_Party/Documents/"
        "PolicyPapers/Manifesto_2024/For_a_Fair_Deal_-_Liberal_Democrat_Manifesto_2024.pdf"
    ),
    ("2019-12-12", "Conservative"): (
        "http://www.cpa.org.uk/cpa/docs/Election2019/ConservativeManifesto2019.pdf"
    ),
}


@dataclass(frozen=True, slots=True)
class PartyManifestoSource:
    party_name: str
    party_short_name: str | None
    election_date: str
    title: str
    source_url: str


def build_party_manifesto_sources() -> list[PartyManifestoSource]:
    sources: list[PartyManifestoSource] = []
    for year, election_date in ELECTION_DATES.items():
        for code in ELECTION_PARTY_CODES[year]:
            party_name, short_name = _party_info(code)
            official = OFFICIAL_PDF_URLS.get((election_date, party_name))
            archive = f"{ARCHIVE_BASE_URL}/man{year}{code}.pdf"
            source_url = official or archive
            sources.append(
                PartyManifestoSource(
                    party_name=party_name,
                    party_short_name=short_name,
                    election_date=election_date,
                    title=f"{year} {party_name} manifesto",
                    source_url=source_url,
                )
            )
    return sources


async def fetch_pdf_text(url: str, *, timeout: float = 120.0) -> str | None:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return extract_pdf_text(response.content)


def extract_pdf_text(content: bytes) -> str | None:
    reader = PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())
    if not pages:
        return None
    return "\n\n".join(pages)


def _party_info(code: str) -> tuple[str, str | None]:
    if code in PARTY_CATALOG:
        return PARTY_CATALOG[code]
    return EXTRA_PARTY_NAMES[code]
