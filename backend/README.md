# backend

Python package for policritique — async data collection, SQLAlchemy persistence, and CLI.

## Setup

```bash
cd backend
cp .env.template .env
uv sync
uv run policritique init-db
```

Configuration: `src/policritique/settings.py` (pydantic-settings).

## CLI (`policritique`)

```bash
uv run policritique init-db
uv run policritique collect-elections
uv run policritique collect-elections --parliament 59
uv run policritique collect-members
uv run policritique collect-manifestos
uv run policritique-api
```

Imports candidacy-level results from [UK Parliament psephology CSVs](https://github.com/ukparliament/psephology) (general elections 2010–2024, parliament periods 55–59).

`collect-members` imports current Commons MPs from the [Members API](https://members-api.parliament.uk) and contact details from the [MNIS Addresses dataset](http://data.parliament.uk/membersdataplatform/memberquery.aspx).

`collect-manifestos` imports coded manifesto text from the [Manifesto Project API](https://manifesto-project.wzb.eu/information/documents/api) (requires `MANIFESTO_PROJECT_API_KEY`) and extracts text from official party PDFs plus the [Politics Resources archive](https://www.politicsresources.net/area/uk/man.htm) for elections since 2010.

## API (`policritique-api`)

JWT-authenticated REST API on `http://127.0.0.1:8000` (see `/docs` for OpenAPI).

| Prefix | Description |
|--------|-------------|
| `/auth` | Register (`POST /auth/register`) |
| `/auth/jwt` | Login (`POST /auth/jwt/login`) |
| `/users` | Current user profile |
| `/parties` | Political parties |
| `/elections` | Elections and `/elections/{id}/results` |
| `/constituencies` | Parliamentary constituencies |
| `/members` | MPs with contacts and terms |
| `/manifestos` | Party manifestos (full text on detail) |

## Database

SQLite at `backend/data/policritique.db` (override with `DB_PATH` in `.env`).

Tables:

| Table | Purpose |
|-------|---------|
| `parties` | Registered political parties |
| `elections` | General and by-elections |
| `constituencies` | Parliamentary constituencies |
| `election_results` | Candidate-level results |
| `members` | MPs and peers |
| `member_terms` | Party / constituency membership over time |
| `member_contacts` | Email, office, website, social |
| `manifestos` | Party policy documents |
| `sync_log` | Collection audit trail |

Schema reference: `../scripts/db/schema.sql`

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check src
uv run ruff format src
```

Run from the `backend/` directory.

## Settings

| Variable | Default |
|----------|---------|
| `DB_PATH` | `backend/data/policritique.db` |
| `MEMBERS_API_BASE_URL` | `https://members-api.parliament.uk` |
| `PARLIAMENT_DATA_BASE_URL` | `http://data.parliament.uk/membersdataplatform` |
| `DEMOCRACY_CLUB_API_BASE_URL` | `https://candidates.democracyclub.org.uk` |
| `PSEPHOLOGY_BASE_URL` | `https://raw.githubusercontent.com/ukparliament/psephology/main/db/data` |
| `MANIFESTO_PROJECT_API_KEY` | *(required for Manifesto Project import)* |
| `MANIFESTO_PROJECT_BASE_URL` | `https://manifesto-project.wzb.eu/api/v1` |
| `MANIFESTO_PROJECT_CORE_VERSION` | `MPDS2025a` |
| `MANIFESTO_PROJECT_METADATA_VERSION` | `2025-1` |
| `SECRET_KEY` | `change-me-in-production` |
| `JWT_LIFETIME_SECONDS` | `3600` |
| `CORS_ORIGINS` | Vite (`5173`), Next (`3000`), and API (`8000`) on `localhost` and `127.0.0.1` |
| `API_HOST` | `127.0.0.1` |
| `API_PORT` | `8000` |
| `API_RELOAD` | `false` |
