"""Pydantic schemas for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PartyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ec_id: str | None
    name: str
    short_name: str | None
    electoral_register: str | None = Field(validation_alias="register")
    collected_at: str


class ElectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    election_type: str
    election_date: str
    parliament_period: str | None
    source: str | None
    collected_at: str


class ConstituencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gss_code: str | None
    country: str | None
    valid_from: str | None
    valid_to: str | None
    collected_at: str


class MemberContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_type: str
    value: str
    is_primary: bool
    collected_at: str

    @field_validator("is_primary", mode="before")
    @classmethod
    def int_to_bool(cls, value: int | bool) -> bool:
        return bool(value)


class MemberTermOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    constituency_id: int | None
    party_id: int | None
    house: str
    start_date: str | None
    end_date: str | None
    collected_at: str


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parliament_member_id: int | None
    name: str
    display_name: str | None
    gender: str | None
    is_current: bool
    collected_at: str

    @field_validator("is_current", mode="before")
    @classmethod
    def int_to_bool(cls, value: int | bool) -> bool:
        return bool(value)


class MemberDetailOut(MemberOut):
    contacts: list[MemberContactOut] = Field(default_factory=list)
    terms: list[MemberTermOut] = Field(default_factory=list)


class ElectionResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    election_id: int
    constituency_id: int
    party_id: int | None
    member_id: int | None
    candidate_name: str
    votes: int | None
    vote_share: float | None
    is_elected: bool
    collected_at: str

    @field_validator("is_elected", mode="before")
    @classmethod
    def int_to_bool(cls, value: int | bool) -> bool:
        return bool(value)


class ManifestoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    party_id: int
    election_id: int | None
    title: str
    source_url: str | None
    published_at: str | None
    collected_at: str


class ManifestoDetailOut(ManifestoOut):
    text: str | None


class PaginatedParties(BaseModel):
    items: list[PartyOut]
    limit: int
    offset: int
    count: int


class PaginatedElections(BaseModel):
    items: list[ElectionOut]
    limit: int
    offset: int
    count: int


class PaginatedConstituencies(BaseModel):
    items: list[ConstituencyOut]
    limit: int
    offset: int
    count: int


class PaginatedMembers(BaseModel):
    items: list[MemberOut]
    limit: int
    offset: int
    count: int


class PaginatedElectionResults(BaseModel):
    items: list[ElectionResultOut]
    limit: int
    offset: int
    count: int


class PaginatedManifestos(BaseModel):
    items: list[ManifestoOut]
    limit: int
    offset: int
    count: int
