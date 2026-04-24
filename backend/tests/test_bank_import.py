from app.schemas import AppSettings, CashDocumentType
from app.services.importers.bank import parse_bank_rows
from app.services.importers.file_readers import read_tabular_bytes


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


def test_bank_csv_reader_handles_cp1250_preamble():
    payload = """
mBank S.A. Bankowość Detaliczna;

#Data księgowania;#Data operacji;#Opis operacji;#Tytuł;#Nadawca/Odbiorca;#Numer konta;#Kwota;#Saldo po operacji;
2026-03-10;2026-03-10;BLIK WYPŁATA ATM WŁASNY;mbank; ;'';-4000,00;32000,00;
""".strip().encode("cp1250")

    rows = read_tabular_bytes("mbank.csv", payload)

    assert len(rows) == 1
    assert rows[0]["#Opis operacji"] == "BLIK WYPŁATA ATM WŁASNY"
    assert rows[0]["#Kwota"] == "-4000,00"


def test_bank_parser_recognizes_mbank_atm_operations():
    result = parse_bank_rows(
        [
            {
                "#Data operacji": "2026-03-10",
                "#Opis operacji": "BLIK WYPŁATA ATM WŁASNY",
                "#Kwota": "-4000,00",
            }
        ],
        AppSettings(bank_party_name_short="BANK", bank_party_name_full="Podmiot bankowy"),
    )

    assert len(result.documents) == 1
    assert result.documents[0].document_type == CashDocumentType.KW
    assert result.unsupported == 0
