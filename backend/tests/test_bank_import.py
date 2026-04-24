from app.schemas import AppSettings, CashDocumentType
from app.services.importers.bank import parse_bank_rows


def test_bank_atm_withdrawal_creates_kw():
    result = parse_bank_rows(
        [
            {
                "Data operacji": "2026-04-24",
                "Opis": "Wyplata z bankomatu",
                "Kwota": "-300,00",
            }
        ],
        AppSettings(bank_party_name_short="BANK", bank_party_name_full="Podmiot bankowy"),
    )

    assert len(result.documents) == 1
    assert result.documents[0].document_type == CashDocumentType.KW
    assert result.documents[0].title == "wyplata z bankomatu z dnia 24-04-2026"


def test_bank_unknown_operation_is_unsupported():
    result = parse_bank_rows(
        [
            {
                "Data operacji": "2026-04-24",
                "Opis": "Oplata za prowadzenie rachunku",
                "Kwota": "10,00",
            }
        ],
        AppSettings(),
    )

    assert result.unsupported == 1
    assert result.documents == []

