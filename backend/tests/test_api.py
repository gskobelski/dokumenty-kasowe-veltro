import httpx
import pytest

from app.main import create_app


def build_client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_health_endpoint(tmp_path):
    async with build_client(tmp_path) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_export_returns_error_without_ready_documents(tmp_path):
    async with build_client(tmp_path) as client:
        response = await client.get("/api/export/epp")
    assert response.status_code == 400
    assert response.json()["detail"] == "No valid documents ready for export"


@pytest.mark.anyio
async def test_settings_can_be_updated(tmp_path):
    async with build_client(tmp_path) as client:
        response = await client.put(
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
    assert response.status_code == 200
    assert response.json()["company_name"] == "Biuro Test"
