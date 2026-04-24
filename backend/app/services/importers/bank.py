from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.schemas import AppSettings, CashDocumentCreate, CashDocumentType, RecipientType, SourceType
from app.services.importers.base import find_value, normalize_text
from app.services.importers.saldeo import ImportResult


def parse_bank_rows(rows: list[dict[str, object]], settings: AppSettings) -> ImportResult:
    result = ImportResult()
    for index, row in enumerate(rows):
        operation_date = find_value(row, ["data operacji", "data", "operation date"])
        description = normalize_text(
            " ".join(
                value
                for value in [
                    find_value(row, ["opis operacji", "opis", "description"]),
                    find_value(row, ["tytul", "title"]),
                ]
                if value
            )
        )
        amount_raw = find_value(row, ["kwota", "amount", "wartosc"])

        document_type = _classify_bank_row(description)
        if document_type is None:
            result.unsupported += 1
            result.raw_results.append(
                {
                    "row_index": index,
                    "classification": "unsupported",
                    "processing_status": "unsupported",
                    "error_reason": "unsupported_bank_operation",
                    "raw_payload": row,
                }
            )
            continue

        issue_date = _parse_date(operation_date)
        title = _build_title(document_type, issue_date)
        recipient_full = settings.bank_party_name_full or settings.bank_party_name_short
        recipient_short = settings.bank_party_name_short or recipient_full[:40]

        cash_document = CashDocumentCreate(
            source_type=SourceType.BANK,
            source_reference=f"{issue_date.isoformat()}-{index}",
            document_type=document_type,
            issue_date=issue_date,
            amount=abs(_parse_amount(amount_raw)),
            title=title,
            description="",
            recipient_type=RecipientType.ONE_TIME_CONTRACTOR,
            recipient_name_short=recipient_short[:40],
            recipient_name_full=recipient_full[:80],
            recipient_city=settings.bank_party_city,
            recipient_postal_code=settings.bank_party_postal_code,
            recipient_address_line=settings.bank_party_address_line,
            recipient_tax_id=settings.bank_party_tax_id,
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


def _classify_bank_row(description: str) -> CashDocumentType | None:
    if any(marker in description for marker in ["prow.", "prowizja"]):
        return None

    if _looks_like_atm_deposit(description):
        return CashDocumentType.KP
    if _looks_like_atm_withdrawal(description):
        return CashDocumentType.KW
    return None


def _looks_like_atm_deposit(description: str) -> bool:
    deposit_markers = ["wplata do bankomatu", "wplata w bankomacie", "atm wplata", "deposit"]
    if any(marker in description for marker in deposit_markers):
        return True
    return "wplata" in description and ("atm" in description or "bankomat" in description)


def _looks_like_atm_withdrawal(description: str) -> bool:
    withdrawal_markers = [
        "wyplata z bankomatu",
        "wyplata w bankomacie",
        "atm wyplata",
        "withdrawal",
    ]
    if any(marker in description for marker in withdrawal_markers):
        return True
    return "wyplata" in description and ("atm" in description or "bankomat" in description)


def _build_title(document_type: CashDocumentType, issue_date) -> str:
    date_text = issue_date.strftime("%d-%m-%Y")
    if document_type == CashDocumentType.KP:
        return f"wplata do bankomatu z dnia {date_text}"
    return f"wyplata z bankomatu z dnia {date_text}"


def _parse_amount(value: str) -> Decimal:
    cleaned = value.replace(" ", "").replace(",", ".")
    return Decimal(cleaned or "0")


def _parse_date(value: str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return datetime.utcnow().date()
