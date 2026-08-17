from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from wind_calculations.datasets.wind_loadf import (
    lookup_internal_pressure_coefficient,
    lookup_low_rise_main_structural_cgcp,
    lookup_low_slope_roof_components_cladding_cgcp,
)
from wind_calculations.exceptions import EngineeringInputError


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LowRiseMainStructuralLookupRequest(StrictModel):
    load_case: Literal["A", "B"]
    roof_slope: float = Field(ge=0, le=60)
    surface: Literal["1", "1E", "2", "2E", "3", "3E", "4", "4E", "5", "5E", "6", "6E"]


class ComponentsCladdingLookupRequest(StrictModel):
    zone: Literal["-C", "-OC", "-OS", "-OR", "-S", "-R", "+S", "+R", "+C"]
    area: float = Field(gt=0)


class InternalPressureLookupRequest(StrictModel):
    category: Literal[0, 1, 2, 3]
    sign: Literal["positive", "negative"]


router = APIRouter(prefix="/api/v1/lookups", tags=["lookups"])


def _engineering_error(exc: EngineeringInputError) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={"code": "ENGINEERING_INPUT_ERROR", "message": str(exc)},
    )


@router.post("/low-rise/main-structural/cgcp")
def low_rise_main_structural_cgcp(request: LowRiseMainStructuralLookupRequest) -> dict[str, object]:
    try:
        value = lookup_low_rise_main_structural_cgcp(
            load_case=request.load_case,
            roof_slope=request.roof_slope,
            surface=request.surface,
        )
    except EngineeringInputError as exc:
        raise _engineering_error(exc) from exc
    return {
        "cgcp": value,
        "load_case": request.load_case,
        "roof_slope": request.roof_slope,
        "surface": request.surface,
        "source": "wind_loadf (1).xlsx - Sheet1",
    }


@router.post("/components-cladding/low-slope-roof/cgcp")
def components_cladding_cgcp(request: ComponentsCladdingLookupRequest) -> dict[str, object]:
    try:
        value = lookup_low_slope_roof_components_cladding_cgcp(zone=request.zone, area=request.area)
    except EngineeringInputError as exc:
        raise _engineering_error(exc) from exc
    return {
        "cgcp": value,
        "zone": request.zone,
        "actual_area": request.area,
        "lookup_area": min(max(request.area, 1.0), 100.0),
        "source": "wind_loadf (1).xlsx - Sheet2",
    }


@router.post("/internal-pressure/cpi")
def internal_pressure_cpi(request: InternalPressureLookupRequest) -> dict[str, object]:
    try:
        value = lookup_internal_pressure_coefficient(category=request.category, sign=request.sign)
    except EngineeringInputError as exc:
        raise _engineering_error(exc) from exc
    return {
        "cpi": value,
        "category": request.category,
        "sign": request.sign,
        "source": "wind_loadf (1).xlsx - Sheet3a",
    }
