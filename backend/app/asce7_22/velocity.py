"""ASCE 7-22 velocity-pressure arithmetic, US customary units.

This is not an ASCE wind speed map or exposure coefficient selector.
Inputs Kz, Kzt, Ke, V are supplied by a qualified upstream selector.
For the ASCE 7-22 Chapter 27 directional procedure, Kd is applied
in the design pressure equation, not twice in velocity pressure.
"""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class VelocityPressureInput:
    ultimate_wind_speed_mph: float
    exposure_coefficient_kz: float
    topographic_factor_kzt: float = 1.0
    ground_elevation_factor_ke: float = 1.0


def velocity_pressure_psf(data: VelocityPressureInput) -> float:
    """Return q = 0.00256 * Kz * Kzt * Ke * V**2 (psf)."""
    for name, value in vars(data).items():
        if not isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    return (0.00256 * data.exposure_coefficient_kz
            * data.topographic_factor_kzt
            * data.ground_elevation_factor_ke
            * data.ultimate_wind_speed_mph ** 2)
