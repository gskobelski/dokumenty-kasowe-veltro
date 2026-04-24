# dokumenty-kasowe-veltro

MVP aplikacji do obslugi dokumentow kasowych KP/KW dla biura ksiegowego.

## Zakres

- import faktur gotowkowych z Saldeo (`CSV`, `XLSX`)
- import wyciagow bankowych (`CSV`, `XLSX`) z klasyfikacja operacji bankomatowych
- przeglad i korekta dokumentow kasowych przed eksportem
- eksport pliku `.epp` zgodnego z EDI++ dla Rewizora GT

## Struktura

- `frontend/` - Next.js UI
- `backend/` - FastAPI API, walidacja, importery i generator `.epp`
- `.ai/specs/` - specyfikacje funkcjonalne

## Backend

Uruchomienie lokalne po zainstalowaniu zaleznosci:

```bash
cd backend
python3 -m uvicorn app.main:app --reload
```

Testy backendu:

```bash
cd backend
python3 -m pytest
```

## Frontend

Uruchomienie lokalne po zainstalowaniu zaleznosci:

```bash
cd frontend
npm install
npm run dev
```

## Eksport EPP

Endpoint eksportu:

```text
GET /api/export/epp
```

Plik nalezy wczytac w Rewizorze GT:

```text
Narzedzia -> Import -> Plik komunikacji
```
