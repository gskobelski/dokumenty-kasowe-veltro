from __future__ import annotations

import csv
from datetime import UTC, date, datetime
from decimal import Decimal
from io import StringIO

from app.config import Settings
from app.schemas import AppSettings, CashDocumentRead, DocumentStatus, RecipientType


def _format_date(value: date | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def _format_bool(value: bool) -> str:
    return "1" if value else "0"


def _format_decimal(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


def _recipient_type_code(recipient_type: RecipientType) -> str:
    mapping = {
        RecipientType.CONTRACTOR: "1",
        RecipientType.EMPLOYEE: "2",
        RecipientType.OFFICE: "3",
        RecipientType.ONE_TIME_CONTRACTOR: "4",
    }
    return mapping[recipient_type]


def _status_code(status: DocumentStatus) -> str:
    return "1" if status == DocumentStatus.EXECUTED else "0"


def _info_fields(settings: Settings, app_settings: AppSettings) -> list[str]:
    return [
        settings.edi_version,
        str(settings.communication_goal),
        str(settings.code_page),
        settings.program_name,
        "",
        app_settings.company_name_short or app_settings.company_name,
        app_settings.company_name,
        app_settings.company_city,
        app_settings.company_postal_code,
        app_settings.company_address_line,
        app_settings.company_tax_id,
        "",
        "",
        "",
        "",
        "0",
        "",
        "",
        "",
        datetime.now(UTC).date().isoformat(),
        "Polska",
        "",
        "",
        "0",
    ]


def _header_fields(document: CashDocumentRead, app_settings: AppSettings) -> list[str]:
    recipient_code = document.recipient_code or document.recipient_pesel or ""

    fields = [
        document.document_type.value,
        _status_code(document.document_status),
        "",
        "",
        _format_date(document.issue_date),
        _recipient_type_code(document.recipient_type),
        recipient_code,
        document.recipient_name_short,
        document.recipient_name_full,
        document.recipient_city,
        document.recipient_postal_code,
        document.recipient_address_line,
        document.recipient_tax_id,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        document.category_name,
        document.category_subtitle,
        document.title,
        _format_bool(document.is_generated),
        _format_date(document.related_issue_date),
        document.comment or document.description,
        document.notes,
        _format_decimal(Decimal("0")),
        _format_decimal(document.amount),
        "0",
        "",
        "",
        "",
        document.issuer_name,
        document.receiver_name,
        app_settings.cash_register_code,
        app_settings.cash_register_name,
        app_settings.cash_register_analytics,
        "",
        "Polska" if document.recipient_name_full else "",
        "",
        "0",
    ]
    return fields


def render_epp(
    documents: list[CashDocumentRead],
    settings: Settings,
    app_settings: AppSettings,
) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    buffer.write("[INFO]\n")
    writer.writerow(_info_fields(settings, app_settings))
    for document in documents:
        buffer.write("[NAGLOWEK]\n")
        writer.writerow(_header_fields(document, app_settings))
    buffer.write("\n")
    return buffer.getvalue()
