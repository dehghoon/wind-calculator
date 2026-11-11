"""Numerical MWFRS directional surface envelope, not code load combinations.

Requires independently validated ASCE coefficients and velocity pressures.
"""
from dataclasses import dataclass
from math import isfinite

from .directional import DirectionalCase, DirectionalSurface, calculate_directional_cases

DIRECTIONS = ("+X", "-X", "+Y", "-Y")


@dataclass(frozen=True)
class SurfaceEnvelope:
    surface: str
    minimum_psf: float
    maximum_psf: float
    minimum_case: str
    maximum_case: str


def directional_envelope(
    surfaces_by_direction: dict[str, list[DirectionalSurface]],
    q_internal_psf: float,
    gust_factor_g: float,
    directionality_factor_kd: float,
    internal_gcpi_magnitude: float,
) -> tuple[list[DirectionalCase], list[SurfaceEnvelope]]:
    """Evaluate four directions x two signs of internal pressure.

    Identical surface names are enveloped across directions; no geometric
    correspondence is inferred. This is not a full ASCE 7-22 MWFRS design.
    """
    if set(surfaces_by_direction) != set(DIRECTIONS):
        raise ValueError("exactly +X, -X, +Y, -Y directions are required")
    cases: list[DirectionalCase] = []
    for direction in DIRECTIONS:
        cases.extend(calculate_directional_cases(
            surfaces_by_direction[direction], q_internal_psf, gust_factor_g,
            directionality_factor_kd, internal_gcpi_magnitude, direction,
        ))
    observations: dict[str, list[tuple[float, str]]] = {}
    for case in cases:
        sign = "+GCpi" if case.internal_gcpi >= 0 else "-GCpi"
        for surface, pressure in case.surface_pressures_psf.items():
            if not isfinite(pressure):
                raise ValueError("nonfinite pressure result")
            observations.setdefault(surface, []).append(
                (pressure, f"{case.direction}/{sign}")
            )
    envelopes = []
    for surface in sorted(observations):
        values = observations[surface]
        low = min(values, key=lambda pair: pair[0])
        high = max(values, key=lambda pair: pair[0])
        envelopes.append(SurfaceEnvelope(surface, low[0], high[0], low[1], high[1]))
    return cases, envelopes
