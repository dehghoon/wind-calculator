"""Independent arithmetic regression; not an ASCE design verification."""
import math
import pytest

from app.asce7_22.velocity import VelocityPressureInput, velocity_pressure_psf
from app.asce7_22.directional import DirectionalSurface, calculate_directional_cases


def test_velocity_pressure_known_arithmetic():
    assert velocity_pressure_psf(VelocityPressureInput(115, 1.0)) == pytest.approx(33.856)


@pytest.mark.parametrize("v", [0, -5, float("nan"), float("inf")])
def test_velocity_rejects_invalid_speed(v):
    with pytest.raises(ValueError):
        velocity_pressure_psf(VelocityPressureInput(v, 1.0))


def test_directional_internal_signs_and_kd_applied_once():
    surfaces = [
        DirectionalSurface("windward", 0.8, 30.0),
        DirectionalSurface("leeward", -0.5, 35.0),
    ]
    positive, negative = calculate_directional_cases(
        surfaces, 35.0, 0.85, 0.85, 0.18, "+X"
    )
    assert positive.surface_pressures_psf["windward"] == pytest.approx(
        0.85 * (30 * 0.85 * 0.8 - 35 * 0.18)
    )
    assert negative.surface_pressures_psf["windward"] == pytest.approx(
        0.85 * (30 * 0.85 * 0.8 + 35 * 0.18)
    )
    assert positive.surface_pressures_psf["leeward"] < 0


@pytest.mark.parametrize("direction", ["+X", "-X", "+Y", "-Y"])
def test_four_directions(direction):
    a, b = calculate_directional_cases(
        [DirectionalSurface("roof", -0.7, 40)], 40, 0.85, 0.85, 0.18, direction
    )
    assert a.direction == b.direction == direction
    assert a.internal_gcpi == 0.18
    assert b.internal_gcpi == -0.18


def test_rejects_duplicate_surfaces():
    with pytest.raises(ValueError):
        calculate_directional_cases(
            [DirectionalSurface("wall", 0.8, 20), DirectionalSurface("wall", -0.5, 20)],
            20, 0.85, 0.85, 0.18, "+X"
        )
