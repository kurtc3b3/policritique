"""Manifesto Project API client and parsers."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from policritique.settings import get_settings

UK_COUNTRY_CODES = {51, 52}
DEFAULT_CORE_VERSION = "MPDS2025a"
DEFAULT_METADATA_VERSION = "2025-1"
BATCH_SIZE = 25


@dataclass(frozen=True, slots=True)
class ManifestoProjectRecord:
    query_key: str
    party_id: int
    party_name: str
    date_yyyymm: int
    title: str | None


@dataclass(frozen=True, slots=True)
class ManifestoProjectDocument:
    manifesto_id: str
    party_name: str
    date_yyyymm: int
    title: str
    source_url: str | None
    text: str


class ManifestoProjectClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        core_version: str | None = None,
        metadata_version: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.manifesto_project_api_key
        self.base_url = (base_url or settings.manifesto_project_base_url).rstrip("/")
        self.core_version = core_version or settings.manifesto_project_core_version
        self.metadata_version = metadata_version or settings.manifesto_project_metadata_version
        self.timeout = timeout

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError(
                "MANIFESTO_PROJECT_API_KEY is required. "
                "Register at https://manifesto-project.wzb.eu and add the key to .env"
            )
        return self.api_key

    async def fetch_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | bool] | None = None,
        method: str = "GET",
        form: list[tuple[str, str]] | None = None,
    ) -> dict:
        api_key = self.require_api_key()
        url = f"{self.base_url}/{path.lstrip('/')}"
        query = {"api_key": api_key, **(params or {})}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            if method == "POST":
                if form:
                    response = await client.post(
                        url,
                        params=query,
                        content=encode_form_data(form),
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                else:
                    response = await client.post(url, params=query)
            else:
                response = await client.get(url, params=query)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object from {url}")
            return payload

    async def fetch_core_csv(self) -> str:
        api_key = self.require_api_key()
        url = f"{self.base_url}/get_core"
        params = {"key": self.core_version, "raw": "true", "api_key": api_key}
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.text

    async def fetch_uk_records(self) -> list[ManifestoProjectRecord]:
        csv_text = await self.fetch_core_csv()
        return parse_core_csv(csv_text)

    async def fetch_metadata(self, keys: list[str]) -> list[dict]:
        if not keys:
            return []
        form = [("keys[]", key) for key in keys]
        payload = await self.fetch_json(
            "/metadata",
            params={"version": self.metadata_version},
            method="POST",
            form=form,
        )
        items = payload.get("items") or []
        return [item for item in items if isinstance(item, dict)]

    async def fetch_texts(self, keys: list[str], *, translation: str = "en") -> list[dict]:
        if not keys:
            return []
        form = [("keys[]", key) for key in keys]
        payload = await self.fetch_json(
            "/texts_and_annotations",
            params={"version": self.metadata_version, "translation": translation},
            method="POST",
            form=form,
        )
        items = payload.get("items") or []
        return [item for item in items if isinstance(item, dict)]

    async def collect_uk_documents(self) -> list[ManifestoProjectDocument]:
        records = await self.fetch_uk_records()
        documents: list[ManifestoProjectDocument] = []

        for offset in range(0, len(records), BATCH_SIZE):
            batch = records[offset : offset + BATCH_SIZE]
            metadata_items = await self.fetch_metadata([record.query_key for record in batch])
            metadata_by_key = {
                key: item
                for item in metadata_items
                if (key := metadata_query_key(item))
            }

            text_keys: list[str] = []
            text_context: dict[str, tuple[ManifestoProjectRecord, dict]] = {}
            for record in batch:
                metadata = metadata_by_key.get(record.query_key, {})
                manifesto_id = _optional_str(metadata.get("manifesto_id")) or record.query_key
                text_keys.append(manifesto_id)
                text_context[manifesto_id] = (record, metadata)

            for text_offset in range(0, len(text_keys), BATCH_SIZE):
                text_batch = text_keys[text_offset : text_offset + BATCH_SIZE]
                text_items = await self.fetch_texts(text_batch)
                for item in text_items:
                    manifesto_id = _optional_str(item.get("key") or item.get("manifesto_id"))
                    if not manifesto_id or manifesto_id not in text_context:
                        continue
                    record, metadata = text_context[manifesto_id]
                    text = extract_corpus_text(item)
                    if not text:
                        continue
                    documents.append(
                        ManifestoProjectDocument(
                            manifesto_id=manifesto_id,
                            party_name=record.party_name,
                            date_yyyymm=record.date_yyyymm,
                            title=_optional_str(metadata.get("title"))
                            or record.title
                            or f"{record.party_name} manifesto {record.date_yyyymm}",
                            source_url=_optional_str(metadata.get("url_original")),
                            text=text,
                        )
                    )

        return documents


def metadata_query_key(item: dict) -> str | None:
    key = _optional_str(item.get("key") or item.get("query_key"))
    if key:
        return key
    party_id = item.get("party_id")
    election_date = item.get("election_date")
    if party_id is not None and election_date is not None:
        return f"{party_id}_{election_date}"
    return None


def encode_form_data(fields: list[tuple[str, str]]) -> str:
    """URL-encode repeated form fields for httpx AsyncClient POST bodies."""
    return urlencode(fields, doseq=True)


def parse_core_csv(text: str) -> list[ManifestoProjectRecord]:
    reader = csv.DictReader(io.StringIO(text))
    records: list[ManifestoProjectRecord] = []
    for row in reader:
        country = _parse_int(row.get("country"))
        if country not in UK_COUNTRY_CODES:
            continue
        party_id = _parse_int(row.get("party"))
        date_yyyymm = _parse_int(row.get("date"))
        if party_id is None or date_yyyymm is None:
            continue
        party_name = (row.get("partyname") or row.get("party_name") or "Unknown").strip()
        query_key = f"{party_id}_{date_yyyymm}"
        records.append(
            ManifestoProjectRecord(
                query_key=query_key,
                party_id=party_id,
                party_name=party_name,
                date_yyyymm=date_yyyymm,
                title=_optional_str(row.get("title")),
            )
        )
    return records


def extract_corpus_text(item: dict) -> str | None:
    items = item.get("items")
    if isinstance(items, list):
        parts = []
        for entry in items:
            if not isinstance(entry, dict):
                continue
            text = entry.get("text")
            if text:
                parts.append(str(text).strip())
        if parts:
            return "\n".join(parts)

    for key in ("text", "content", "body"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list):
            parts = [str(part).strip() for part in value if str(part).strip()]
            if parts:
                return "\n".join(parts)

    annotations = item.get("annotations")
    if isinstance(annotations, list):
        parts = []
        for annotation in annotations:
            if not isinstance(annotation, dict):
                continue
            text = annotation.get("text") or annotation.get("value")
            if text:
                parts.append(str(text).strip())
        if parts:
            return "\n".join(parts)

    return None


def published_at_from_yyyymm(date_yyyymm: int) -> str:
    year = date_yyyymm // 100
    month = date_yyyymm % 100
    return f"{year}-{month:02d}-01"


def election_year_from_yyyymm(date_yyyymm: int) -> int:
    return date_yyyymm // 100


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    return int(float(str(value).strip()))
