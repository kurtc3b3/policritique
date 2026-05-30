# frontend

Vite + React UI for querying UK political data from the policritique API.

## Setup

```bash
cd frontend
yarn install
cp .env.example .env
yarn dev
```

Open [http://localhost:5173](http://localhost:5173).

## Backend

The UI expects the FastAPI backend at `VITE_API_URL` (default `http://127.0.0.1:8000`).

```bash
cd ../backend
uv run policritique-api
```

Ensure backend `CORS_ORIGINS` includes your frontend origin (defaults cover `http://localhost:5173` and `http://127.0.0.1:5173`). If you created `backend/.env` before the frontend was added, update `CORS_ORIGINS` or re-copy from `.env.template`.

Register a user at `/register`, then browse elections, MPs, parties, constituencies, and manifestos.

## Scripts

| Command | Description |
|---------|-------------|
| `yarn dev` | Development server |
| `yarn build` | Production build |
| `yarn preview` | Preview production build |
