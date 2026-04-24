from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.schemas import (
    AppSettings,
    CashDocumentCreate,
    CashDocumentRead,
    CashDocumentUpdate,
    ImportSessionSummary,
    PrepareExportResponse,
    ValidationStatus,
)
from app.services.validation import derive_validation_status, validate_document


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def init_schema(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    company_name TEXT NOT NULL DEFAULT '',
                    company_name_short TEXT NOT NULL DEFAULT '',
                    company_city TEXT NOT NULL DEFAULT '',
                    company_postal_code TEXT NOT NULL DEFAULT '',
                    company_address_line TEXT NOT NULL DEFAULT '',
                    company_tax_id TEXT NOT NULL DEFAULT '',
                    cash_register_code TEXT NOT NULL DEFAULT 'KASA',
                    cash_register_name TEXT NOT NULL DEFAULT 'Kasa glowna',
                    cash_register_analytics TEXT NOT NULL DEFAULT '',
                    bank_party_name_short TEXT NOT NULL DEFAULT 'BANK',
                    bank_party_name_full TEXT NOT NULL DEFAULT 'Podmiot bankowy',
                    bank_party_city TEXT NOT NULL DEFAULT '',
                    bank_party_postal_code TEXT NOT NULL DEFAULT '',
                    bank_party_address_line TEXT NOT NULL DEFAULT '',
                    bank_party_tax_id TEXT NOT NULL DEFAULT ''
                );
                INSERT OR IGNORE INTO app_settings(id) VALUES (1);

                CREATE TABLE IF NOT EXISTS import_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    imported_at TEXT NOT NULL,
                    row_count INTEGER NOT NULL DEFAULT 0,
                    created_documents_count INTEGER NOT NULL DEFAULT 0,
                    ignored_rows_count INTEGER NOT NULL DEFAULT 0,
                    unsupported_rows_count INTEGER NOT NULL DEFAULT 0,
                    review_required_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS cash_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_session_id INTEGER,
                    source_type TEXT NOT NULL,
                    source_reference TEXT NOT NULL DEFAULT '',
                    document_type TEXT NOT NULL,
                    document_status TEXT NOT NULL,
                    issue_date TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    recipient_type TEXT NOT NULL,
                    recipient_code TEXT NOT NULL DEFAULT '',
                    recipient_name_short TEXT NOT NULL DEFAULT '',
                    recipient_name_full TEXT NOT NULL DEFAULT '',
                    recipient_city TEXT NOT NULL DEFAULT '',
                    recipient_postal_code TEXT NOT NULL DEFAULT '',
                    recipient_address_line TEXT NOT NULL DEFAULT '',
                    recipient_tax_id TEXT NOT NULL DEFAULT '',
                    recipient_pesel TEXT NOT NULL DEFAULT '',
                    category_name TEXT NOT NULL DEFAULT '',
                    category_subtitle TEXT NOT NULL DEFAULT '',
                    issuer_name TEXT NOT NULL DEFAULT '',
                    receiver_name TEXT NOT NULL DEFAULT '',
                    is_generated INTEGER NOT NULL DEFAULT 0,
                    related_issue_date TEXT,
                    comment TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    validation_status TEXT NOT NULL DEFAULT 'requires_review',
                    validation_errors TEXT NOT NULL DEFAULT '[]',
                    ready_for_export INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS import_rows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_session_id INTEGER NOT NULL,
                    row_index INTEGER NOT NULL,
                    raw_payload TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    processing_status TEXT NOT NULL,
                    cash_document_id INTEGER,
                    error_reason TEXT NOT NULL DEFAULT ''
                );
                """
            )

    def get_settings(self) -> AppSettings:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM app_settings WHERE id = 1").fetchone()
        return AppSettings.model_validate(dict(row))

    def save_settings(self, settings: AppSettings) -> AppSettings:
        payload = settings.model_dump()
        columns = ", ".join(f"{key} = ?" for key in payload)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE app_settings SET {columns} WHERE id = 1",
                list(payload.values()),
            )
        return self.get_settings()

    def create_import_session(self, source_type: str, filename: str, row_count: int) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO import_sessions(
                    source_type, filename, imported_at, row_count
                ) VALUES (?, ?, ?, ?)
                """,
                (source_type, filename, datetime.now(UTC).isoformat(), row_count),
            )
            return int(cursor.lastrowid)

    def complete_import_session(
        self,
        session_id: int,
        created_documents_count: int,
        ignored_rows_count: int,
        unsupported_rows_count: int,
        review_required_count: int,
    ) -> ImportSessionSummary:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE import_sessions
                SET created_documents_count = ?,
                    ignored_rows_count = ?,
                    unsupported_rows_count = ?,
                    review_required_count = ?
                WHERE id = ?
                """,
                (
                    created_documents_count,
                    ignored_rows_count,
                    unsupported_rows_count,
                    review_required_count,
                    session_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM import_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        return ImportSessionSummary.model_validate(_convert_row(dict(row)))

    def insert_import_row(
        self,
        session_id: int,
        row_index: int,
        raw_payload: dict[str, Any],
        classification: str,
        processing_status: str,
        cash_document_id: int | None,
        error_reason: str,
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO import_rows(
                    import_session_id, row_index, raw_payload, classification,
                    processing_status, cash_document_id, error_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    row_index,
                    json.dumps(raw_payload, ensure_ascii=False),
                    classification,
                    processing_status,
                    cash_document_id,
                    error_reason,
                ),
            )

    def create_cash_document(self, document: CashDocumentCreate) -> CashDocumentRead:
        now = datetime.now(UTC).isoformat()
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO cash_documents(
                    import_session_id, source_type, source_reference, document_type,
                    document_status, issue_date, amount, title, description,
                    recipient_type, recipient_code, recipient_name_short, recipient_name_full,
                    recipient_city, recipient_postal_code, recipient_address_line,
                    recipient_tax_id, recipient_pesel, category_name, category_subtitle,
                    issuer_name, receiver_name, is_generated, related_issue_date,
                    comment, notes, ready_for_export, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.import_session_id,
                    document.source_type.value,
                    document.source_reference,
                    document.document_type.value,
                    document.document_status.value,
                    document.issue_date.isoformat(),
                    str(document.amount),
                    document.title,
                    document.description,
                    document.recipient_type.value,
                    document.recipient_code,
                    document.recipient_name_short,
                    document.recipient_name_full,
                    document.recipient_city,
                    document.recipient_postal_code,
                    document.recipient_address_line,
                    document.recipient_tax_id,
                    document.recipient_pesel,
                    document.category_name,
                    document.category_subtitle,
                    document.issuer_name,
                    document.receiver_name,
                    int(document.is_generated),
                    document.related_issue_date.isoformat() if document.related_issue_date else None,
                    document.comment,
                    document.notes,
                    int(document.ready_for_export),
                    now,
                    now,
                ),
            )
            doc_id = int(cursor.lastrowid)
        return self.revalidate_document(doc_id)

    def list_cash_documents(self, filters: dict[str, str]) -> list[CashDocumentRead]:
        clauses: list[str] = []
        params: list[Any] = []
        if filters.get("document_type"):
            clauses.append("document_type = ?")
            params.append(filters["document_type"])
        if filters.get("source_type"):
            clauses.append("source_type = ?")
            params.append(filters["source_type"])
        if filters.get("validation_status"):
            clauses.append("validation_status = ?")
            params.append(filters["validation_status"])
        if filters.get("search"):
            search = f"%{filters['search']}%"
            clauses.append(
                "(title LIKE ? OR source_reference LIKE ? OR recipient_name_full LIKE ?)"
            )
            params.extend([search, search, search])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM cash_documents {where} ORDER BY issue_date DESC, id DESC",
                params,
            ).fetchall()
        return [self._row_to_document(dict(row)) for row in rows]

    def get_cash_document(self, document_id: int) -> CashDocumentRead | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM cash_documents WHERE id = ?",
                (document_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_document(dict(row))

    def update_cash_document(
        self,
        document_id: int,
        payload: CashDocumentUpdate,
    ) -> CashDocumentRead | None:
        updates = {
            key: value
            for key, value in payload.model_dump(exclude_none=True).items()
        }
        if not updates:
            return self.get_cash_document(document_id)
        assignments = []
        params: list[Any] = []
        for key, value in updates.items():
            assignments.append(f"{key} = ?")
            if isinstance(value, bool):
                params.append(int(value))
            else:
                params.append(value.value if hasattr(value, "value") else value)
        assignments.append("updated_at = ?")
        params.append(datetime.now(UTC).isoformat())
        params.append(document_id)
        with self.connect() as connection:
            connection.execute(
                f"UPDATE cash_documents SET {', '.join(assignments)} WHERE id = ?",
                params,
            )
        return self.revalidate_document(document_id)

    def revalidate_document(self, document_id: int) -> CashDocumentRead:
        document = self.get_cash_document(document_id)
        if document is None:
            raise KeyError(document_id)
        errors = validate_document(document)
        ready = int(not errors and document.ready_for_export)
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE cash_documents
                SET validation_status = ?, validation_errors = ?, ready_for_export = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    derive_validation_status(errors).value,
                    json.dumps(errors),
                    ready,
                    datetime.now(UTC).isoformat(),
                    document_id,
                ),
            )
        refreshed = self.get_cash_document(document_id)
        if refreshed is None:
            raise KeyError(document_id)
        return refreshed

    def list_ready_documents(self) -> list[CashDocumentRead]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM cash_documents
                WHERE ready_for_export = 1 AND validation_status = ?
                ORDER BY issue_date, id
                """,
                (ValidationStatus.VALID.value,),
            ).fetchall()
        return [self._row_to_document(dict(row)) for row in rows]

    def prepare_bank_documents_for_export(self) -> PrepareExportResponse:
        settings = self.get_settings()
        bank_documents = [
            document
            for document in self.list_cash_documents({})
            if document.source_type == "bank"
        ]

        for document in bank_documents:
            payload = CashDocumentUpdate(
                recipient_name_short=document.recipient_name_short or settings.bank_party_name_short,
                recipient_name_full=document.recipient_name_full or settings.bank_party_name_full,
                recipient_city=document.recipient_city or settings.bank_party_city,
                recipient_postal_code=document.recipient_postal_code or settings.bank_party_postal_code,
                recipient_address_line=document.recipient_address_line or settings.bank_party_address_line,
                recipient_tax_id=document.recipient_tax_id or settings.bank_party_tax_id,
                ready_for_export=True,
            )
            self.update_cash_document(document.id, payload)

        refreshed = [
            document
            for document in self.list_cash_documents({})
            if document.source_type == "bank"
        ]
        ready_count = sum(
            1
            for document in refreshed
            if document.ready_for_export and document.validation_status == ValidationStatus.VALID
        )
        blocked_count = len(refreshed) - ready_count
        return PrepareExportResponse(
            total_bank_documents=len(refreshed),
            ready_count=ready_count,
            blocked_count=blocked_count,
        )

    def list_validation_errors(self) -> dict[str, int]:
        counters: dict[str, int] = {}
        for document in self.list_cash_documents({}):
            for error in document.validation_errors:
                counters[error] = counters.get(error, 0) + 1
        return counters

    def _row_to_document(self, row: dict[str, Any]) -> CashDocumentRead:
        converted = _convert_row(row)
        return CashDocumentRead.model_validate(converted)


def _convert_row(row: dict[str, Any]) -> dict[str, Any]:
    for key, value in list(row.items()):
        if key in {"created_at", "updated_at", "imported_at"} and value:
            row[key] = datetime.fromisoformat(value)
        elif key in {"issue_date", "related_issue_date"} and value:
            row[key] = date.fromisoformat(value)
        elif key == "amount":
            row[key] = Decimal(value)
        elif key in {"ready_for_export", "is_generated"}:
            row[key] = bool(value)
        elif key == "validation_errors":
            row[key] = json.loads(value or "[]")
    return row
