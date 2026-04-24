from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_db
from app.db import Database
from app.schemas import CashDocumentRead, CashDocumentUpdate, ValidationErrorSummary

router = APIRouter(tags=["documents"])


@router.get("", response_model=list[CashDocumentRead])
def list_documents(
    document_type: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    validation_status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Database = Depends(get_db),
) -> list[CashDocumentRead]:
    filters = {
        key: value
        for key, value in {
            "document_type": document_type,
            "source_type": source_type,
            "validation_status": validation_status,
            "search": search,
        }.items()
        if value
    }
    return db.list_cash_documents(filters)


@router.get("/validation-errors", response_model=list[ValidationErrorSummary])
def list_validation_errors(db: Database = Depends(get_db)) -> list[ValidationErrorSummary]:
    counters = db.list_validation_errors()
    return [
        ValidationErrorSummary(code=code, count=count)
        for code, count in sorted(counters.items())
    ]


@router.get("/{document_id}", response_model=CashDocumentRead)
def get_document(document_id: int, db: Database = Depends(get_db)) -> CashDocumentRead:
    document = db.get_cash_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.patch("/{document_id}", response_model=CashDocumentRead)
def update_document(
    document_id: int,
    payload: CashDocumentUpdate,
    db: Database = Depends(get_db),
) -> CashDocumentRead:
    document = db.update_cash_document(document_id, payload)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

