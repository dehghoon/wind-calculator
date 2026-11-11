"""ASCE 7-22 MWFRS directional pressure assembly (limited).

Coefficients and velocity pressures MUST be independently verified upstream
against the governing standard. This module does not select ASCE Cp, GCpi,
exposure, topography, wind speed, or generate MIDAS load cases.
No MIDAS source or release artifacts are incorporated.
"""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class DirectionalPressureInput:
    q_external_psf: float
    q_internal_psf: float
    gust_factor: float
    external_cp: float
    internal_gcpi: float


def net_pressure_psf(data: DirectionalPressureInput) -> float:
    """Compute p = q_external*G*Cp - q_internal*GCpi, in psf.

    Caller is responsible for selecting correct q(z) or q(h) and coefficients.
    """
    for name, value in vars(data).items():
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if data.q_external_psf < 0 or data.q_internal_psf < 0:
        raise ValueError("velocity pressures must be nonnegative")
    if data.gust_factor <= 0:
        raise ValueError("gust_factor must be positive")
    return (data.q_external_psf * data.gust_factor * data.external_cp
            - data.q_internal_psf * data.internal_gcpi)
