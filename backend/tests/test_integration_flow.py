import httpx
import pytest

from app.main import create_app


@pytest.mark.anyio
async def test_import_edit_export_flow(tmp_path):
    app = create_app(str(tmp_path / "flow.db"))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.put(
            "/api/settings",
            json={
                "company_name": "Biuro Test",
                "company_name_short": "BT",
                "company_city": "Warszawa",
                "company_postal_code": "00-001",
                "company_address_line": "Testowa 1",
                "company_tax_id": "9999999999",
                "cash_register_code": "KASA",
                "cash_register_name": "Kasa glowna",
                "cash_register_analytics": "K01",
                "bank_party_name_short": "BANK",
                "bank_party_name_full": "Podmiot bankowy",
                "bank_party_city": "Warszawa",
                "bank_party_postal_code": "00-950",
                "bank_party_address_line": "Bankowa 1",
                "bank_party_tax_id": "1111111111",
            },
        )
        files = {
            "file": (
                "saldeo.csv",
                "Numer faktury;Data;Kontrahent;Kwota brutto;Forma platnosci;Typ dokumentu\nFV/1/2026;2026-04-24;ABC Sp. z o.o.;123,45;Gotowka;Faktura sprzedazy\n",
                "text/csv",
            )
        }
        import_response = await client.post("/api/imports/saldeo", files=files)
        assert import_response.status_code == 200
        documents_response = await client.get("/api/documents")
        document_id = documents_response.json()[0]["id"]
        update_response = await client.patch(
            f"/api/documents/{document_id}",
            json={
                "recipient_city": "Warszawa",
                "recipient_postal_code": "00-001",
                "recipient_address_line": "Testowa 1",
                "ready_for_export": True,
            },
        )
        assert update_response.status_code == 200
        assert update_response.json()["validation_status"] == "valid"
        export_response = await client.get("/api/export/epp")
        assert export_response.status_code == 200
        assert "[INFO]" in export_response.text
        assert "[NAGLOWEK]" in export_response.text
