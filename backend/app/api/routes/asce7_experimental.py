"""Explicit-input ASCE 7-22 arithmetic sandbox. Disabled unless opted in.

NOT a complete or verified ASCE 7-22 design calculation. Values are
supplied by the caller; this endpoint never selects coefficients or wind maps.
"""
import os
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from app.asce7_22.velocity import VelocityPressureInput, velocity_pressure_psf
from app.asce7_22.directional import DirectionalSurface, calculate_directional_cases

router = APIRouter(prefix="/api/v1/asce7-22", tags=["experimental-asce7"])


class SurfaceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=80)
    cp: float = Field(ge=-10, le=10)
    kz: float = Field(gt=0, le=10)


class ExperimentalDirectionalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ultimate_wind_speed_mph: float = Field(gt=0, le=300)
    topographic_factor_kzt: float = Field(gt=0, le=10)
    ground_elevation_factor_ke: float = Field(gt=0, le=10)
    internal_exposure_coefficient_kz: float = Field(gt=0, le=10)
    gust_factor_g: float = Field(gt=0, le=10)
    directionality_factor_kd: float = Field(gt=0, le=1)
    internal_gcpi_magnitude: float = Field(ge=0, le=2)
    direction: Literal["+X", "-X", "+Y", "-Y"]
    surfaces: list[SurfaceInput] = Field(min_length=1, max_length=40)


@router.post("/experimental/directional")
def experimental_directional(request: ExperimentalDirectionalRequest) -> dict:
    if os.getenv("ASCE7_EXPERIMENTAL_ENABLED", "").lower() != "true":
        raise HTTPException(status_code=404, detail="Experimental route disabled")
    try:
        base = dict(
            ultimate_wind_speed_mph=request.ultimate_wind_speed_mph,
            topographic_factor_kzt=request.topographic_factor_kzt,
            ground_elevation_factor_ke=request.ground_elevation_factor_ke,
        )
        q_internal = velocity_pressure_psf(VelocityPressureInput(
            **base, exposure_coefficient_kz=request.internal_exposure_coefficient_kz
        ))
        surfaces = [
            DirectionalSurface(
                name=s.name,
                external_cp=s.cp,
                q_external_psf=velocity_pressure_psf(VelocityPressureInput(
                    **base, exposure_coefficient_kz=s.kz
                )),
            )
            for s in request.surfaces
        ]
        cases = calculate_directional_cases(
            surfaces=surfaces,
            q_internal_psf=q_internal,
            gust_factor_g=request.gust_factor_g,
            directionality_factor_kd=request.directionality_factor_kd,
            internal_gcpi_magnitude=request.internal_gcpi_magnitude,
            direction=request.direction,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "status": "UNVERIFIED_ARITHMETIC_ONLY",
        "code_edition": "ASCE_7_22",
        "unit": "psf",
        "warning": "Not for engineering design. Cp/Kz/GCpi and applicability are not selected or verified.",
        "cases": [
            {
                "direction": case.direction,
                "internal_gcpi": case.internal_gcpi,
                "surface_pressures_psf": case.surface_pressures_psf,
            }
            for case in cases
        ],
    }
