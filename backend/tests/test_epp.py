import csv
from datetime import UTC, date, datetime
from decimal import Decimal
from io import StringIO

from app.config import Settings
from app.schemas import (
    AppSettings,
    CashDocumentRead,
    CashDocumentType,
    DocumentStatus,
    RecipientType,
    SourceType,
    ValidationStatus,
)
from app.services.epp import render_epp


def test_export_includes_info_and_header_sections():
    document = CashDocumentRead(
        id=1,
        import_session_id=1,
        source_type=SourceType.SALDEO,
        source_reference="FV/2/2026",
        document_type=CashDocumentType.KP,
        document_status=DocumentStatus.EXECUTED,
        issue_date=date(2026, 4, 24),
        amount=Decimal("100.00"),
        title="wplata za fakture FV/2/2026",
        description="",
        recipient_type=RecipientType.CONTRACTOR,
        recipient_code="",
        recipient_name_short="ABC",
        recipient_name_full="ABC Sp. z o.o.",
        recipient_city="Warszawa",
        recipient_postal_code="00-001",
        recipient_address_line="Testowa 1",
        recipient_tax_id="1234567890",
        recipient_pesel="",
        category_name="",
        category_subtitle="",
        issuer_name="Jan Kowalski",
        receiver_name="Anna Nowak",
        is_generated=False,
        related_issue_date=None,
        comment="",
        notes="",
        ready_for_export=True,
        validation_status=ValidationStatus.VALID,
        validation_errors=[],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    settings = Settings()
    app_settings = AppSettings(
        company_name="Biuro Test",
        company_name_short="BT",
        company_city="Warszawa",
        company_postal_code="00-001",
        company_address_line="Testowa 1",
        company_tax_id="9999999999",
        cash_register_code="KASA",
        cash_register_name="Kasa glowna",
    )
    payload = render_epp([document], settings, app_settings)

    assert payload.startswith("[INFO]\n")
    assert payload.count("[NAGLOWEK]") == 1

    lines = [line for line in payload.splitlines() if line and not line.startswith("[")]
    info_fields = next(csv.reader([lines[0]]))
    header_fields = next(csv.reader([lines[1]]))

    assert len(info_fields) == 24
    assert len(header_fields) == 56
    assert header_fields[0] == "KP"
    assert header_fields[1] == "1"
    assert header_fields[42] == "100.00"
    assert header_fields[49] == "KASA"
