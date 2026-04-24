from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.api.deps import get_db
from app.config import get_settings
from app.db import Database
from app.services.epp import render_epp

router = APIRouter(tags=["export"])


@router.get("/epp")
def export_epp(db: Database = Depends(get_db)) -> PlainTextResponse:
    documents = db.list_ready_documents()
    if not documents:
        raise HTTPException(status_code=400, detail="No valid documents ready for export")
    payload = render_epp(documents, get_settings(), db.get_settings())
    headers = {"Content-Disposition": 'attachment; filename="cash-documents.epp"'}
    return PlainTextResponse(payload, media_type="text/plain; charset=windows-1250", headers=headers)

