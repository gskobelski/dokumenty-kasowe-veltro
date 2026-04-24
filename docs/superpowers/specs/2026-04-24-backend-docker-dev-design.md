# Backend Docker Dev Design

## Goal

Ustawić środowisko developerskie tak, żeby frontend działał lokalnie przez `npm run dev`, a backend był uruchamiany przez `docker compose up` z hot-reloadem.

## Desired Workflow

- Frontend:
  - `cd frontend`
  - `npm run dev`
- Backend:
  - `cd backend`
  - `docker compose up`

## Design

### Backend Container

- Dodać `backend/Dockerfile` oparty o `python:3.13-slim`
- Instalować zależności backendu z `pyproject.toml`
- Uruchamiać `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### Docker Compose

- Dodać `backend/compose.yaml`
- Zmapować port `8000:8000`
- Zamontować katalog `backend/` do kontenera jako volume, żeby `--reload` widział lokalne zmiany
- Ustawić `DATABASE_PATH` na plik w katalogu projektu backendu

### Repo Hygiene

- Dodać `backend/.dockerignore`, żeby obraz nie zawierał `.venv`, cache i lokalnej bazy
- Zaktualizować `README.md` o nowy sposób uruchamiania

## Verification

- `cd backend && docker compose config`
- `cd backend && docker compose up --build`
- `cd frontend && npm run build`
