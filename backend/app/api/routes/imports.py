from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_db
from app.db import Database
from app.schemas import ImportResponse, SourceType
from app.services.importers.bank import parse_bank_rows
from app.services.importers.file_readers import read_tabular_bytes
from app.services.importers.saldeo import parse_saldeo_rows

router = APIRouter(tags=["imports"])


@router.post("/saldeo", response_model=ImportResponse)
async def import_saldeo(
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
) -> ImportResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    payload = await file.read()
    rows = read_tabular_bytes(file.filename, payload)
    session_id = db.create_import_session(SourceType.SALDEO.value, file.filename, len(rows))
    result = parse_saldeo_rows(rows)
    for raw in result.raw_results:
        doc_id = None
        if raw["processing_status"] == "created":
            document = result.documents.pop(0)
            document.import_session_id = session_id
            created = db.create_cash_document(document)
            doc_id = created.id
        db.insert_import_row(
            session_id=session_id,
            row_index=int(raw["row_index"]),
            raw_payload=dict(raw["raw_payload"]),
            classification=str(raw["classification"]),
            processing_status=str(raw["processing_status"]),
            cash_document_id=doc_id,
            error_reason=str(raw["error_reason"]),
        )
    session = db.complete_import_session(
        session_id,
        created_documents_count=sum(1 for raw in result.raw_results if raw["processing_status"] == "created"),
        ignored_rows_count=result.ignored,
        unsupported_rows_count=result.unsupported,
        review_required_count=result.review_required,
    )
    return ImportResponse(
        session=session,
        documents_created=session.created_documents_count,
        review_required=session.review_required_count,
        unsupported=session.unsupported_rows_count,
    )


@router.post("/bank", response_model=ImportResponse)
async def import_bank(
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
) -> ImportResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    payload = await file.read()
    rows = read_tabular_bytes(file.filename, payload)
    session_id = db.create_import_session(SourceType.BANK.value, file.filename, len(rows))
    result = parse_bank_rows(rows, db.get_settings())
    for raw in result.raw_results:
        doc_id = None
        if raw["processing_status"] == "created":
            document = result.documents.pop(0)
            document.import_session_id = session_id
            created = db.create_cash_document(document)
            doc_id = created.id
        db.insert_import_row(
            session_id=session_id,
            row_index=int(raw["row_index"]),
            raw_payload=dict(raw["raw_payload"]),
            classification=str(raw["classification"]),
            processing_status=str(raw["processing_status"]),
            cash_document_id=doc_id,
            error_reason=str(raw["error_reason"]),
        )
    session = db.complete_import_session(
        session_id,
        created_documents_count=sum(1 for raw in result.raw_results if raw["processing_status"] == "created"),
        ignored_rows_count=result.ignored,
        unsupported_rows_count=result.unsupported,
        review_required_count=result.review_required,
    )
    return ImportResponse(
        session=session,
        documents_created=session.created_documents_count,
        review_required=session.review_required_count,
        unsupported=session.unsupported_rows_count,
    )

