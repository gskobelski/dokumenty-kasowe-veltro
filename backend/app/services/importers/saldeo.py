from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from app.schemas import (
    CashDocumentCreate,
    CashDocumentType,
    RecipientType,
    SourceType,
)
from app.services.importers.base import find_value, normalize_text


@dataclass(slots=True)
class ImportResult:
    documents: list[CashDocumentCreate] = field(default_factory=list)
    review_required: int = 0
    ignored: int = 0
    unsupported: int = 0
    raw_results: list[dict[str, object]] = field(default_factory=list)


def parse_saldeo_rows(rows: list[dict[str, object]]) -> ImportResult:
    result = ImportResult()
    for index, row in enumerate(rows):
        invoice_number = find_value(row, ["numer faktury", "nr faktury", "numer", "invoice number"])
        issue_date_raw = find_value(row, ["data", "data platnosci", "data dokumentu", "payment date"])
        counterparty = find_value(row, ["kontrahent", "nazwa kontrahenta", "nabywca", "customer"])
        payment_method = normalize_text(find_value(row, ["forma platnosci", "platnosc", "payment method"]))
        doc_kind = normalize_text(find_value(row, ["typ dokumentu", "rodzaj dokumentu", "typ", "document type"]))
        amount_raw = find_value(row, ["kwota brutto", "brutto", "amount", "wartosc brutto"])

        if "got" not in payment_method:
            result.ignored += 1
            result.raw_results.append(
                {
                    "row_index": index,
                    "classification": "ignored",
                    "processing_status": "ignored",
                    "error_reason": "payment_not_cash",
                    "raw_payload": row,
                }
            )
            continue

        document_type = _classify_saldeo_document(doc_kind)
        if document_type is None:
            result.review_required += 1
            result.raw_results.append(
                {
                    "row_index": index,
                    "classification": "requires_review",
                    "processing_status": "requires_review",
                    "error_reason": "unknown_document_kind",
                    "raw_payload": row,
                }
            )
            continue

        cash_document = CashDocumentCreate(
            source_type=SourceType.SALDEO,
            source_reference=invoice_number,
            document_type=document_type,
            issue_date=_parse_date(issue_date_raw),
            amount=_parse_amount(amount_raw),
            title=_build_title(document_type, invoice_number),
            description="",
            recipient_type=RecipientType.CONTRACTOR,
            recipient_name_short=counterparty[:40],
            recipient_name_full=counterparty[:80],
            recipient_city="",
            recipient_postal_code="",
            recipient_address_line="",
            recipient_tax_id=find_value(row, ["nip", "tax id"]),
            ready_for_export=False,
        )
        result.documents.append(cash_document)
        result.raw_results.append(
            {
                "row_index": index,
                "classification": document_type.value,
                "processing_status": "created",
                "error_reason": "",
                "raw_payload": row,
            }
        )
    return result


def _classify_saldeo_document(doc_kind: str) -> CashDocumentType | None:
    revenue_markers = ["przychod", "sprzedaz", "sprzedazy", "fs", "sale", "revenue"]
    cost_markers = ["koszt", "zakup", "fz", "expense", "purchase"]
    if any(marker in doc_kind for marker in revenue_markers):
        return CashDocumentType.KP
    if any(marker in doc_kind for marker in cost_markers):
        return CashDocumentType.KW
    return None


def _build_title(document_type: CashDocumentType, invoice_number: str) -> str:
    if document_type == CashDocumentType.KP:
        return f"wplata za fakture {invoice_number}".strip()
    return f"zaplata za fakture {invoice_number}".strip()


def _parse_amount(value: str) -> Decimal:
    cleaned = value.replace(" ", "").replace(",", ".")
    return Decimal(cleaned or "0")


def _parse_date(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return datetime.utcnow().date()

