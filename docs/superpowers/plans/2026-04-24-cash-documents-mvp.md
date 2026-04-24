# Cash Documents MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an MVP that imports Saldeo and bank statement files, normalizes them into cash documents `KP`/`KW`, allows review and correction, and exports a Rewizor GT compatible `.epp` file.

**Architecture:** The repo will contain a `frontend/` Next.js app and a `backend/` FastAPI app. The backend owns domain rules, parsing, validation, persistence, and `.epp` generation; the frontend is a thin review and import client over the API.

**Tech Stack:** Next.js, React, TypeScript, FastAPI, SQLAlchemy, Pydantic, SQLite, pytest

---

### Task 1: Scaffold Project Structure

**Files:**
- Create: `.gitignore`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.ts`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`

- [ ] **Step 1: Write the failing smoke expectations**

```text
Frontend must expose an app shell with import, documents, export, and settings sections.
Backend must expose `/health` returning `{ "status": "ok" }`.
```

- [ ] **Step 2: Add repository ignore and base manifests**

```gitignore
.DS_Store
.next
node_modules
dist
build
.venv
__pycache__
.pytest_cache
*.pyc
*.db
```

- [ ] **Step 3: Scaffold minimal backend entrypoint**

```python
from fastapi import FastAPI

app = FastAPI(title="Cash Documents API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Scaffold minimal frontend shell**

```tsx
export default function HomePage() {
  return <main>Cash Documents MVP</main>;
}
```

- [ ] **Step 5: Verify basic structure exists**

Run: `find frontend backend -maxdepth 3 -type f | sort`
Expected: frontend and backend manifests plus minimal entry files are present.

### Task 2: Build Backend Domain and EPP Exporter

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/services/epp.py`
- Create: `backend/app/services/validation.py`
- Create: `backend/tests/test_epp.py`
- Create: `backend/tests/test_validation.py`

- [ ] **Step 1: Write failing validation tests**

```python
def test_document_requires_title_for_export():
    ...

def test_valid_document_maps_status_and_recipient_type():
    ...
```

- [ ] **Step 2: Run tests to confirm failure**

Run: `python3 -m pytest backend/tests/test_validation.py backend/tests/test_epp.py`
Expected: tests fail because domain model and exporter do not exist yet.

- [ ] **Step 3: Implement document schema, validation, and EPP serializer**

```python
class CashDocumentType(str, Enum):
    KP = "KP"
    KW = "KW"
```

```python
def render_epp(documents: list[CashDocument]) -> str:
    ...
```

- [ ] **Step 4: Re-run backend unit tests**

Run: `python3 -m pytest backend/tests/test_validation.py backend/tests/test_epp.py`
Expected: validation and EPP tests pass.

### Task 3: Build Saldeo and Bank Import Pipelines

**Files:**
- Create: `backend/app/services/importers/base.py`
- Create: `backend/app/services/importers/saldeo.py`
- Create: `backend/app/services/importers/bank.py`
- Create: `backend/app/services/importers/file_readers.py`
- Create: `backend/tests/test_saldeo_import.py`
- Create: `backend/tests/test_bank_import.py`

- [ ] **Step 1: Write failing importer tests for Saldeo and bank rows**

```python
def test_saldeo_revenue_cash_invoice_creates_kp():
    ...

def test_bank_atm_withdrawal_creates_kw():
    ...
```

- [ ] **Step 2: Run importer tests to verify red state**

Run: `python3 -m pytest backend/tests/test_saldeo_import.py backend/tests/test_bank_import.py`
Expected: tests fail because importers are missing.

- [ ] **Step 3: Implement tolerant CSV/XLSX readers and row normalization**

```python
def parse_saldeo_rows(rows: list[dict[str, Any]]) -> ImportResult:
    ...

def parse_bank_rows(rows: list[dict[str, Any]]) -> ImportResult:
    ...
```

- [ ] **Step 4: Verify importer tests pass**

Run: `python3 -m pytest backend/tests/test_saldeo_import.py backend/tests/test_bank_import.py`
Expected: parser tests pass for supported and unsupported cases.

### Task 4: Expose CRUD and Export API

**Files:**
- Create: `backend/app/api/routes/imports.py`
- Create: `backend/app/api/routes/documents.py`
- Create: `backend/app/api/routes/settings.py`
- Create: `backend/app/api/routes/export.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

```python
def test_health_endpoint():
    ...

def test_export_returns_epp_file_for_valid_documents():
    ...
```

- [ ] **Step 2: Run API tests to verify missing routes**

Run: `python3 -m pytest backend/tests/test_api.py`
Expected: tests fail before routes and wiring are added.

- [ ] **Step 3: Implement API routes and application wiring**

```python
app.include_router(imports_router, prefix="/api/imports")
app.include_router(documents_router, prefix="/api/documents")
app.include_router(export_router, prefix="/api/export")
app.include_router(settings_router, prefix="/api/settings")
```

- [ ] **Step 4: Re-run API tests**

Run: `python3 -m pytest backend/tests/test_api.py`
Expected: API tests pass.

### Task 5: Build Frontend Review Interface

**Files:**
- Create: `frontend/app/import/page.tsx`
- Create: `frontend/app/documents/page.tsx`
- Create: `frontend/app/settings/page.tsx`
- Create: `frontend/components/app-shell.tsx`
- Create: `frontend/components/import-panel.tsx`
- Create: `frontend/components/document-table.tsx`
- Create: `frontend/components/document-editor.tsx`
- Create: `frontend/components/export-panel.tsx`
- Create: `frontend/lib/api.ts`
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/globals.css`

- [ ] **Step 1: Write failing UI expectations as component contracts**

```text
The documents page must show filters, a table of records, and an editor panel.
The import page must expose separate uploads for Saldeo and bank files.
```

- [ ] **Step 2: Implement app shell and route pages**

```tsx
<AppShell>
  <ImportPanel />
  <DocumentTable />
  <ExportPanel />
</AppShell>
```

- [ ] **Step 3: Wire frontend API client to backend endpoints**

```ts
export async function listDocuments(params?: URLSearchParams) {
  ...
}
```

- [ ] **Step 4: Verify source structure**

Run: `find frontend/app frontend/components frontend/lib -maxdepth 3 -type f | sort`
Expected: routes, components, and API client exist.

### Task 6: Integrate, Verify, and Document

**Files:**
- Modify: `.ai/specs/planned-features/cash-documents-mvp.md`
- Create: `README.md`
- Create: `backend/tests/fixtures/sample_saldeo.csv`
- Create: `backend/tests/fixtures/sample_bank.csv`
- Create: `backend/tests/test_integration_flow.py`

- [ ] **Step 1: Write failing integration test**

```python
def test_import_edit_export_flow():
    ...
```

- [ ] **Step 2: Run full backend test suite and observe remaining failures**

Run: `python3 -m pytest backend/tests`
Expected: only integration gaps remain before final wiring.

- [ ] **Step 3: Finish integration wiring and update documentation**

```md
## Development
### Frontend
### Backend
### EPP export
```

- [ ] **Step 4: Re-run full verification**

Run: `python3 -m pytest backend/tests`
Expected: full backend test suite passes.

- [ ] **Step 5: Update spec lifecycle after implementation**

Move planned spec into permanent domain location, update status to `verified`, and remove stale planned entry.
