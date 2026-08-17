from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from wind_calculations.enums import CodeEdition, PressureApplication


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BuildingGeometryRequest(StrictModel):
    height: float = Field(gt=0)
    plan_dimension_b: float = Field(gt=0)
    plan_dimension_w: float = Field(gt=0)
    wind_parallel_dimension: float = Field(gt=0)
    roof_slope: float = Field(ge=0, le=90)


class LowRiseApplicabilityResponse(StrictModel):
    applicable: bool
    height_limit_satisfied: bool
    aspect_ratio_limit_satisfied: bool
    minimum_plan_dimension: float
    height_to_minimum_plan_dimension_ratio: float
    unit_system: str = "SI"
    route: str = "WIND-LR"


class ExposureFactorRequest(StrictModel):
    terrain: Literal["open", "rough"]
    reference_height: float = Field(gt=0)


class ExposureFactorResponse(StrictModel):
    exposure_factor: float
    terrain: Literal["open", "rough"]
    reference_height: float
    unit: str = "dimensionless"


class LowRisePressureRequest(StrictModel):
    code_edition: CodeEdition
    importance_factor: float = Field(gt=0)
    reference_velocity_pressure: float = Field(gt=0)
    exposure_factor: float = Field(gt=0)
    gust_pressure_coefficient: float
    height_factor: float = Field(gt=0)


class GeneralStaticCpRequest(StrictModel):
    height: float = Field(gt=0)
    wind_parallel_dimension: float = Field(gt=0)


class GeneralStaticCpResponse(StrictModel):
    windward: float
    leeward: float
    parallel_wall: float
    roof: float
    route: str = "WIND-GS"
    unit_system: str = "SI"


class GeneralStaticPressureRequest(StrictModel):
    code_edition: CodeEdition
    importance_factor: float = Field(gt=0)
    reference_velocity_pressure: float = Field(gt=0)
    exposure_factor: float = Field(gt=0)
    topographic_factor: float = Field(gt=0)
    pressure_application: PressureApplication
    pressure_coefficient: float


class GeneralStaticRunRequest(StrictModel):
    code_edition: CodeEdition
    height: float = Field(gt=0)
    wind_parallel_dimension: float = Field(gt=0)
    terrain: Literal["open", "rough"]
    importance_factor: float = Field(gt=0)
    reference_velocity_pressure: float = Field(gt=0)
    topographic_factor: float = Field(gt=0)
    pressure_application: PressureApplication


class GeneralStaticSurfaceResult(StrictModel):
    cp: float
    pressure: float
    unit: str = "kPa"


class GeneralStaticRunResponse(StrictModel):
    exposure_factor: float
    gust_effect_factor: float
    windward: GeneralStaticSurfaceResult
    leeward: GeneralStaticSurfaceResult
    parallel_wall: GeneralStaticSurfaceResult
    roof: GeneralStaticSurfaceResult
    route: str = "WIND-GS"


class PressureResponse(StrictModel):
    pressure: float
    unit: str = "kPa"


class AreaLookupRequest(StrictModel):
    actual_area: float = Field(gt=0)
    maximum_table_area: float = Field(ge=1)


class AreaLookupResponse(StrictModel):
    actual_area: float
    lookup_area: float
    maximum_table_area: float
    unit: str = "m2"
    route: str = "WIND-CC"


class InterpolationRequest(StrictModel):
    area: float
    area_1: float
    coefficient_1: float
    area_2: float
    coefficient_2: float


class InterpolationResponse(StrictModel):
    coefficient: float
    method: str = "DEC-06 project method"
    route: str = "WIND-CC"
