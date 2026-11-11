"""Arithmetic-only tests; NOT ASCE 7-22 design validation."""
import pytest

from app.asce7_22.pressure import DirectionalPressureInput, net_pressure_psf


@pytest.mark.parametrize(
    "gcpi, expected",
    [(0.18, 24.48), (-0.18, 36.72)],
)
def test_pressure_signs(gcpi, expected):
    data = DirectionalPressureInput(
        q_external_psf=36.0,
        q_internal_psf=34.0,
        gust_factor=0.85,
        external_cp=1.0,
        internal_gcpi=gcpi,
    )
    assert net_pressure_psf(data) == pytest.approx(expected)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_invalid_velocity_pressure(value):
    with pytest.raises(ValueError):
        net_pressure_psf(DirectionalPressureInput(value, 30, 0.85, 0.8, 0.18))


def test_negative_suction():
    assert net_pressure_psf(DirectionalPressureInput(
        40, 40, 0.85, -0.7, 0.18
    )) == pytest.approx(-31.0)
