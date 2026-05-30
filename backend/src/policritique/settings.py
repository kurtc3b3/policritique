"""Application settings loaded from environment and .env file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: Path | None = Field(default=None, validation_alias="DB_PATH")
    members_api_base_url: str = Field(
        default="https://members-api.parliament.uk",
        validation_alias="MEMBERS_API_BASE_URL",
    )
    parliament_data_base_url: str = Field(
        default="http://data.parliament.uk/membersdataplatform",
        validation_alias="PARLIAMENT_DATA_BASE_URL",
    )
    democracy_club_api_base_url: str = Field(
        default="https://candidates.democracyclub.org.uk",
        validation_alias="DEMOCRACY_CLUB_API_BASE_URL",
    )
    psephology_base_url: str = Field(
        default="https://raw.githubusercontent.com/ukparliament/psephology/main/db/data",
        validation_alias="PSEPHOLOGY_BASE_URL",
    )
    manifesto_project_api_key: str | None = Field(
        default=None,
        validation_alias="MANIFESTO_PROJECT_API_KEY",
    )
    manifesto_project_base_url: str = Field(
        default="https://manifesto-project.wzb.eu/api/v1",
        validation_alias="MANIFESTO_PROJECT_BASE_URL",
    )
    manifesto_project_core_version: str = Field(
        default="MPDS2025a",
        validation_alias="MANIFESTO_PROJECT_CORE_VERSION",
    )
    manifesto_project_metadata_version: str = Field(
        default="2025-1",
        validation_alias="MANIFESTO_PROJECT_METADATA_VERSION",
    )
    secret_key: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        validation_alias="SECRET_KEY",
    )
    jwt_lifetime_seconds: int = Field(default=3600, validation_alias="JWT_LIFETIME_SECONDS")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        validation_alias="CORS_ORIGINS",
    )
    api_host: str = Field(default="127.0.0.1", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_reload: bool = Field(default=False, validation_alias="API_RELOAD")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def schema_path(self) -> Path:
        return REPO_ROOT / "scripts" / "db" / "schema.sql"

    @property
    def resolved_db_path(self) -> Path:
        return self.db_path or BACKEND_ROOT / "data" / "policritique.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
