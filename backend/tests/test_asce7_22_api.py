"""Feature-gate and request contract regression for the isolated ASCE sandbox."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PAYLOAD = {
    "ultimate_wind_speed_mph": 115,
    "topographic_factor_kzt": 1,
    "ground_elevation_factor_ke": 1,
    "internal_exposure_coefficient_kz": 1,
    "gust_factor_g": 0.85,
    "directionality_factor_kd": 0.85,
    "internal_gcpi_magnitude": 0.18,
    "direction": "+X",
    "surfaces": [{"name": "windward", "cp": 0.8, "kz": 1}],
}


def test_route_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ASCE7_EXPERIMENTAL_ENABLED", raising=False)
    response = client.post("/api/v1/asce7-22/experimental/directional", json=PAYLOAD)
    assert response.status_code == 404


def test_route_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("ASCE7_EXPERIMENTAL_ENABLED", "true")
    response = client.post("/api/v1/asce7-22/experimental/directional", json=PAYLOAD)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "UNVERIFIED_ARITHMETIC_ONLY"
    assert len(result["cases"]) == 2
    assert result["cases"][0]["surface_pressures_psf"]["windward"] == pytest.approx(
        0.85 * (33.856 * 0.85 * 0.8 - 33.856 * 0.18)
    )


def test_invalid_coefficients_rejected(monkeypatch):
    monkeypatch.setenv("ASCE7_EXPERIMENTAL_ENABLED", "true")
    response = client.post("/api/v1/asce7-22/experimental/directional", json={
        **PAYLOAD, "surfaces": [{"name": "wall", "cp": 0.8, "kz": -1}]
    })
    assert response.status_code == 422
