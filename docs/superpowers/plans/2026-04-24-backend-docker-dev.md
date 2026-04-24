# Backend Docker Dev Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Uruchamiać frontend lokalnie i backend przez `docker compose up` z deweloperskim hot-reloadem.

**Architecture:** Backend dostaje pojedynczy kontener developerski oparty o `python:3.13-slim`, a compose montuje katalog `backend/` do kontenera i wystawia port `8000`. Frontend pozostaje bez zmian runtime, tylko README zostaje dopasowane do nowego workflow.

**Tech Stack:** Docker, Docker Compose, FastAPI, Uvicorn, Python 3.13, Next.js

---

### Task 1: Add backend container files

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/compose.yaml`
- Create: `backend/.dockerignore`

- [ ] **Step 1: Create the Docker image definition**

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 2: Create compose service**

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

- [ ] **Step 3: Exclude local-only files from build context**

```text
.venv
__pycache__
.pytest_cache
*.pyc
*.db
*.egg-info
```

- [ ] **Step 4: Verify compose config**

Run: `cd backend && docker compose config`
Expected: Valid merged compose output with one `backend` service.

### Task 2: Update developer docs

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace backend run instructions**

```md
cd backend
docker compose up
```

- [ ] **Step 2: Keep frontend local workflow explicit**

```md
cd frontend
npm install
npm run dev
```

- [ ] **Step 3: Mention backend rebuild case**

```md
cd backend
docker compose up --build
```

### Task 3: Verify end-to-end startup

**Files:**
- Verify only

- [ ] **Step 1: Run compose validation**

Run: `cd backend && docker compose config`
Expected: PASS

- [ ] **Step 2: Start backend container**

Run: `cd backend && docker compose up --build`
Expected: Uvicorn listening on `0.0.0.0:8000`

- [ ] **Step 3: Run frontend build smoke test**

Run: `cd frontend && npm run build`
Expected: PASS
