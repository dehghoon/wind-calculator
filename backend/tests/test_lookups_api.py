import pytest

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_low_rise_workbook_lookup_endpoint() -> None:
    response = client.post(
        "/api/v1/lookups/low-rise/main-structural/cgcp",
        json={"load_case": "A", "roof_slope": 25.0, "surface": "1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cgcp"] == pytest.approx(1.025)
    assert body["source"].endswith("Sheet1")


def test_components_workbook_lookup_endpoint() -> None:
    response = client.post(
        "/api/v1/lookups/components-cladding/low-slope-roof/cgcp",
        json={"zone": "-C", "area": 7.095337742966286},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cgcp"] == pytest.approx(-2.5066915517926667)
    assert body["lookup_area"] == pytest.approx(7.095337742966286)


def test_internal_pressure_lookup_endpoint() -> None:
    response = client.post(
        "/api/v1/lookups/internal-pressure/cpi",
        json={"category": 3, "sign": "negative"},
    )
    assert response.status_code == 200
    assert response.json()["cpi"] == pytest.approx(-0.7)
