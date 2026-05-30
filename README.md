# policritique

Collect open UK political data — election results, MPs, party policies — and analyse it.

## Quick start

```bash
cd backend
cp .env.template .env
uv sync
uv run policritique init-db
```

Frontend:

```bash
cd frontend
yarn install
cp .env.example .env
yarn dev
```

## Layout

```
policritique/
├── backend/                 # Python package (uv + SQLAlchemy + SQLite)
│   ├── .env.template
│   ├── data/                # SQLite database (gitignored)
│   ├── pyproject.toml
│   └── src/policritique/
├── frontend/                # Vite + React UI (yarn)
└── scripts/
    └── db/schema.sql        # SQL reference (ORM is source of truth)
```

## Data sources

- **Election results** — [UK Parliament psephology CSVs](https://github.com/ukparliament/psephology) (2010–2024)
- **MPs & contacts** — [Members API](https://members-api.parliament.uk/) + [MNIS](http://data.parliament.uk/membersdataplatform)
- **Party policies** — [Manifesto Project API](https://manifesto-project.wzb.eu) + official party PDFs
- **News** — later integration

## Documentation

- [backend/README.md](backend/README.md) — Python CLI and database
- [frontend/README.md](frontend/README.md) — Vite React UI

## Roadmap

- [x] Project setup (uv, SQLAlchemy, SQLite)
- [x] Election results collector
- [x] MP list and contacts collector
- [x] Manifesto / policy collector
- [x] HTTP API (FastAPI + JWT auth)
- [x] Analysis UI
- [ ] News API integration
