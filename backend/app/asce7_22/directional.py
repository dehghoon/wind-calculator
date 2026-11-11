"""Limited ASCE 7-22 directional MWFRS pressure arithmetic.

External pressure: q_external * Kd * G * Cp.
Internal pressure: q_internal * Kd * GCpi.
Only arithmetic; the governing standard controls coefficient applicability.
"""
from dataclasses import dataclass
from math import isfinite

from .velocity import VelocityPressureInput, velocity_pressure_psf


@dataclass(frozen=True)
class DirectionalSurface:
    name: str
    external_cp: float
    q_external_psf: float


@dataclass(frozen=True)
class DirectionalCase:
    direction: str
    internal_gcpi: float
    surface_pressures_psf: dict[str, float]


def calculate_directional_cases(
    surfaces: list[DirectionalSurface],
    q_internal_psf: float,
    gust_factor_g: float,
    directionality_factor_kd: float,
    internal_gcpi_magnitude: float,
    direction: str,
) -> tuple[DirectionalCase, DirectionalCase]:
    """Generate ±GCpi cases for caller-selected surfaces in one wind direction.

    Does not implement Figure 27.3-8 MWFRS combinations or Cp selection.
    """
    if direction not in ("+X", "-X", "+Y", "-Y"):
        raise ValueError("direction must be +X, -X, +Y, or -Y")
    for name, value in (
        ("q_internal_psf", q_internal_psf),
        ("gust_factor_g", gust_factor_g),
        ("directionality_factor_kd", directionality_factor_kd),
        ("internal_gcpi_magnitude", internal_gcpi_magnitude),
    ):
        if not isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if gust_factor_g == 0 or directionality_factor_kd == 0:
        raise ValueError("G and Kd must be positive")
    if not surfaces or len({s.name for s in surfaces}) != len(surfaces):
        raise ValueError("surfaces must be nonempty with unique names")
    for s in surfaces:
        if not s.name or not isfinite(s.external_cp):
            raise ValueError("surface name/Cp invalid")
        if not isfinite(s.q_external_psf) or s.q_external_psf < 0:
            raise ValueError("surface q must be finite and nonnegative")

    result = []
    for sign in (1, -1):
        gcpi = sign * internal_gcpi_magnitude
        pressures = {
            s.name: directionality_factor_kd * (
                s.q_external_psf * gust_factor_g * s.external_cp
                - q_internal_psf * gcpi
            )
            for s in surfaces
        }
        result.append(DirectionalCase(direction, gcpi, pressures))
    return result[0], result[1]
