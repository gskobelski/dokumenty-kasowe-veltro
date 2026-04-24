from app.schemas import CashDocumentType
from app.services.importers.saldeo import parse_saldeo_rows


def test_saldeo_revenue_cash_invoice_creates_kp():
    result = parse_saldeo_rows(
        [
            {
                "Numer faktury": "FV/1/2026",
                "Data": "2026-04-24",
                "Kontrahent": "ABC Sp. z o.o.",
                "Kwota brutto": "123,45",
                "Forma platnosci": "Gotowka",
                "Typ dokumentu": "Faktura sprzedazy",
            }
        ]
    )

    assert len(result.documents) == 1
    assert result.documents[0].document_type == CashDocumentType.KP
    assert result.documents[0].title == "wplata za fakture FV/1/2026"


def test_saldeo_non_cash_invoice_is_ignored():
    result = parse_saldeo_rows(
        [
            {
                "Numer faktury": "FV/2/2026",
                "Data": "2026-04-24",
                "Kontrahent": "ABC Sp. z o.o.",
                "Kwota brutto": "123,45",
                "Forma platnosci": "Przelew",
                "Typ dokumentu": "Faktura sprzedazy",
            }
        ]
    )

    assert result.ignored == 1
    assert result.documents == []

