from datetime import UTC, date, datetime
from decimal import Decimal

from app.schemas import (
    CashDocumentRead,
    CashDocumentType,
    DocumentStatus,
    RecipientType,
    SourceType,
    ValidationStatus,
)
from app.services.validation import derive_validation_status, validate_document


def build_document(**overrides):
    base = {
        "id": 1,
        "source_type": SourceType.SALDEO,
        "source_reference": "FV/1/2026",
        "document_type": CashDocumentType.KP,
        "document_status": DocumentStatus.EXECUTED,
        "issue_date": date(2026, 4, 24),
        "amount": Decimal("123.45"),
        "title": "wplata za fakture FV/1/2026",
        "description": "",
        "recipient_type": RecipientType.CONTRACTOR,
        "recipient_code": "",
        "recipient_name_short": "ABC",
        "recipient_name_full": "ABC Sp. z o.o.",
        "recipient_city": "Warszawa",
        "recipient_postal_code": "00-001",
        "recipient_address_line": "Testowa 1",
        "recipient_tax_id": "1234567890",
        "recipient_pesel": "",
        "category_name": "",
        "category_subtitle": "",
        "issuer_name": "",
        "receiver_name": "",
        "is_generated": False,
        "related_issue_date": None,
        "comment": "",
        "notes": "",
        "ready_for_export": True,
        "import_session_id": 1,
        "validation_status": ValidationStatus.VALID,
        "validation_errors": [],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    base.update(overrides)
    return CashDocumentRead.model_validate(base)


def test_document_requires_title_for_export():
    document = build_document(title=" ")
    errors = validate_document(document)
    assert "missing_title" in errors
    assert derive_validation_status(errors) == ValidationStatus.REQUIRES_REVIEW


def test_valid_document_maps_status_and_recipient_type():
    document = build_document()
    assert validate_document(document) == []
    assert derive_validation_status([]) == ValidationStatus.VALID
