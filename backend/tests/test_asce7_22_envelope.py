"""Numerical arithmetic tests, not ASCE design validation."""
import pytest

from app.asce7_22.directional import DirectionalSurface
from app.asce7_22.envelope import DIRECTIONS, directional_envelope


def test_eight_cases_and_surface_envelope():
    surfaces = {
        direction: [DirectionalSurface("wall", cp, 30.0)]
        for direction, cp in zip(DIRECTIONS, (0.8, -0.5, 0.7, -0.6))
    }
    cases, envelopes = directional_envelope(surfaces, 30, 0.85, 0.85, 0.18)
    assert len(cases) == 8
    assert len(envelopes) == 1
    wall = envelopes[0]
    assert wall.maximum_psf == pytest.approx(0.85 * (30 * 0.85 * 0.8 + 30 * 0.18))
    assert wall.minimum_psf == pytest.approx(0.85 * (30 * 0.85 * -0.6 - 30 * 0.18))
    assert wall.maximum_case == "+X/-GCpi"
    assert wall.minimum_case == "-Y/+GCpi"


def test_missing_direction_rejected():
    with pytest.raises(ValueError, match="exactly"):
        directional_envelope({"+X": [DirectionalSurface("wall", 0.8, 30)]},
                             30, 0.85, 0.85, 0.18)


def test_different_surface_names_allowed():
    surfaces = {
        direction: [DirectionalSurface(direction, 0.8, 30)]
        for direction in DIRECTIONS
    }
    cases, envelopes = directional_envelope(surfaces, 30, 0.85, 0.85, 0.18)
    assert len(cases) == 8
    assert len(envelopes) == 4
