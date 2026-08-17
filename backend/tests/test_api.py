from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_low_rise_boundary_is_preserved() -> None:
    response = client.post(
        "/api/v1/calculations/low-rise/applicability",
        json={
            "height": 20.0,
            "plan_dimension_b": 25.0,
            "plan_dimension_w": 30.0,
            "wind_parallel_dimension": 25.0,
            "roof_slope": 90.0,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["applicable"] is True
    assert body["height_limit_satisfied"] is True


def test_low_rise_ratio_boundary_is_not_applicable() -> None:
    response = client.post(
        "/api/v1/calculations/low-rise/applicability",
        json={
            "height": 20.0,
            "plan_dimension_b": 20.0,
            "plan_dimension_w": 30.0,
            "wind_parallel_dimension": 20.0,
            "roof_slope": 0.0,
        },
    )
    assert response.status_code == 200
    assert response.json()["applicable"] is False


def test_general_static_cp4_strict_boundary() -> None:
    response = client.post(
        "/api/v1/calculations/general-static/cp",
        json={"height": 10.0, "wind_parallel_dimension": 10.0},
    )
    assert response.status_code == 200
    assert response.json()["roof"] == -0.5


def test_nbc2010_general_static_cg_is_not_invented() -> None:
    response = client.post(
        "/api/v1/calculations/general-static/pressure",
        json={
            "code_edition": "NBC_2010",
            "importance_factor": 1.0,
            "reference_velocity_pressure": 0.5,
            "exposure_factor": 1.0,
            "topographic_factor": 1.0,
            "pressure_application": "building_as_whole",
            "pressure_coefficient": 0.8,
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "UNSUPPORTED_ENGINEERING_RULE"


def test_component_area_clamp_retains_actual_area() -> None:
    response = client.post(
        "/api/v1/calculations/components-cladding/area-lookup",
        json={"actual_area": 0.25, "maximum_table_area": 50.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["actual_area"] == 0.25
    assert body["lookup_area"] == 1.0
