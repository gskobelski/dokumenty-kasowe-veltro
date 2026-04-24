# Bank Import Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Naprawić import realnego CSV mBank oraz dodać czytelne statusy procesowania i wyniku importu na ekranie importu.

**Architecture:** Backend dostanie bardziej odporny odczyt CSV i rozszerzoną klasyfikację operacji bankowych. Frontend pozostanie w jednym komponencie importu, ale przejdzie z pojedynczego stringa statusu na jawny model stanów z prostym panelem wyników.

**Tech Stack:** FastAPI, sqlite3, Python, Next.js App Router, React, TypeScript

---

### Task 1: Red tests for mBank CSV parsing

**Files:**
- Modify: `backend/tests/test_bank_import.py`
- Test: `backend/tests/test_bank_import.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_bank_csv_reader_handles_cp1250_preamble():
    ...

def test_bank_parser_recognizes_mbank_atm_operations():
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python3 -m pytest tests/test_bank_import.py -v`
Expected: FAIL on the new mBank parsing assertions.

- [ ] **Step 3: Implement the minimal backend fix**

```python
rows = read_tabular_bytes("mbank.csv", payload)
result = parse_bank_rows(rows, AppSettings(...))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python3 -m pytest tests/test_bank_import.py -v`
Expected: PASS

### Task 2: Harden CSV reader and bank classifier

**Files:**
- Modify: `backend/app/services/importers/file_readers.py`
- Modify: `backend/app/services/importers/bank.py`
- Test: `backend/tests/test_bank_import.py`

- [ ] **Step 1: Add cp1250-aware decoding and header row detection**

```python
def _decode_csv(payload: bytes) -> str:
    ...

def _find_header_row(lines: list[str], delimiter: str) -> int:
    ...
```

- [ ] **Step 2: Extend bank description matching**

```python
description = normalize_text(find_value(row, ["opis operacji", "opis", "tytul", "title"]))
```

- [ ] **Step 3: Normalize ATM markers without diacritics**

```python
if "wplata" in description and "atm" in description:
    ...
```

- [ ] **Step 4: Run targeted tests**

Run: `cd backend && python3 -m pytest tests/test_bank_import.py tests/test_api.py -v`
Expected: PASS

### Task 3: Add import progress and result states in UI

**Files:**
- Modify: `frontend/components/import-panel.tsx`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/components/types.ts`

- [ ] **Step 1: Introduce explicit import status model**

```tsx
type ImportState =
  | { kind: "idle" }
  | { kind: "processing"; source: string; fileName: string }
  | { kind: "success" | "warning"; ... }
  | { kind: "error"; ... };
```

- [ ] **Step 2: Render status card with icon, title and summary**

```tsx
<section className="panel import-status">...</section>
```

- [ ] **Step 3: Disable the active button and show spinner while processing**

```tsx
<button disabled={isProcessing}>...</button>
```

- [ ] **Step 4: Run frontend build**

Run: `cd frontend && npm run build`
Expected: PASS

### Task 4: Full verification

**Files:**
- Verify only

- [ ] **Step 1: Run full backend test suite**

Run: `cd backend && python3 -m pytest tests`
Expected: PASS

- [ ] **Step 2: Run frontend production build**

Run: `cd frontend && npm run build`
Expected: PASS

- [ ] **Step 3: Verify real file import**

Run: `curl -i -F "file=@/Users/gracjanskobelski/Downloads/84442804_260301_260331.csv" http://127.0.0.1:8000/api/imports/bank`
Expected: `documents_created` greater than `0` and a non-error HTTP response.
