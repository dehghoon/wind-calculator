from fastapi import APIRouter, HTTPException

from wind_calculations import BuildingGeometry
from wind_calculations.calculations.components_cladding import (
    clamp_component_area_for_lookup,
    logarithmic_difference_interpolation,
)
from wind_calculations.calculations.general_static import (
    calculate_general_static_pressure,
    calculate_leeward_cp,
    calculate_parallel_wall_cp,
    calculate_roof_cp,
    calculate_windward_cp,
    select_general_static_gust_effect_factor,
)
from wind_calculations.calculations.low_rise import (
    calculate_low_rise_external_pressure,
    calculate_open_terrain_exposure_factor,
    calculate_rough_terrain_exposure_factor,
    is_low_rise_applicable,
)
from wind_calculations.exceptions import (
    EngineeringInputError,
    UnsupportedEngineeringRuleError,
)

from app.schemas.calculations import (
    AreaLookupRequest,
    AreaLookupResponse,
    BuildingGeometryRequest,
    ExposureFactorRequest,
    ExposureFactorResponse,
    GeneralStaticCpRequest,
    GeneralStaticCpResponse,
    GeneralStaticPressureRequest,
    GeneralStaticRunRequest,
    GeneralStaticRunResponse,
    GeneralStaticSurfaceResult,
    InterpolationRequest,
    InterpolationResponse,
    LowRiseApplicabilityResponse,
    LowRisePressureRequest,
    PressureResponse,
)

router = APIRouter(prefix="/api/v1/calculations", tags=["calculations"])


def _translate_engine_error(exc: Exception) -> HTTPException:
    if isinstance(exc, UnsupportedEngineeringRuleError):
        return HTTPException(
            status_code=422,
            detail={
                "code": "UNSUPPORTED_ENGINEERING_RULE",
                "message": str(exc),
            },
        )
    return HTTPException(
        status_code=422,
        detail={
            "code": "ENGINEERING_INPUT_ERROR",
            "message": str(exc),
        },
    )


@router.post(
    "/low-rise/applicability",
    response_model=LowRiseApplicabilityResponse,
)
def low_rise_applicability(
    request: BuildingGeometryRequest,
) -> LowRiseApplicabilityResponse:
    try:
        geometry = BuildingGeometry(**request.model_dump())
        result = is_low_rise_applicable(geometry)
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc

    return LowRiseApplicabilityResponse(
        applicable=result.applicable,
        height_limit_satisfied=result.height_limit_satisfied,
        aspect_ratio_limit_satisfied=result.aspect_ratio_limit_satisfied,
        minimum_plan_dimension=result.minimum_plan_dimension,
        height_to_minimum_plan_dimension_ratio=(
            result.height_to_minimum_plan_dimension_ratio
        ),
    )


@router.post("/exposure-factor", response_model=ExposureFactorResponse)
def exposure_factor(request: ExposureFactorRequest) -> ExposureFactorResponse:
    try:
        if request.terrain == "open":
            value = calculate_open_terrain_exposure_factor(request.reference_height)
        else:
            value = calculate_rough_terrain_exposure_factor(request.reference_height)
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc

    return ExposureFactorResponse(
        exposure_factor=value,
        terrain=request.terrain,
        reference_height=request.reference_height,
    )


@router.post("/low-rise/external-pressure", response_model=PressureResponse)
def low_rise_external_pressure(request: LowRisePressureRequest) -> PressureResponse:
    try:
        pressure = calculate_low_rise_external_pressure(
            importance_factor=request.importance_factor,
            reference_velocity_pressure=request.reference_velocity_pressure,
            exposure_factor=request.exposure_factor,
            gust_pressure_coefficient=request.gust_pressure_coefficient,
            height_factor=request.height_factor,
        )
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc
    return PressureResponse(pressure=pressure)


@router.post("/general-static/cp", response_model=GeneralStaticCpResponse)
def general_static_cp(request: GeneralStaticCpRequest) -> GeneralStaticCpResponse:
    try:
        h = request.height
        d = request.wind_parallel_dimension
        return GeneralStaticCpResponse(
            windward=calculate_windward_cp(h, d),
            leeward=calculate_leeward_cp(h, d),
            parallel_wall=calculate_parallel_wall_cp(),
            roof=calculate_roof_cp(h, d),
        )
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc


@router.post("/general-static/pressure", response_model=PressureResponse)
def general_static_pressure(
    request: GeneralStaticPressureRequest,
) -> PressureResponse:
    try:
        gust_effect_factor = select_general_static_gust_effect_factor(
            request.code_edition,
            request.pressure_application,
        )
        pressure = calculate_general_static_pressure(
            importance_factor=request.importance_factor,
            reference_velocity_pressure=request.reference_velocity_pressure,
            exposure_factor=request.exposure_factor,
            topographic_factor=request.topographic_factor,
            gust_effect_factor=gust_effect_factor,
            pressure_coefficient=request.pressure_coefficient,
        )
    except (EngineeringInputError, UnsupportedEngineeringRuleError) as exc:
        raise _translate_engine_error(exc) from exc
    return PressureResponse(pressure=pressure)


@router.post("/general-static/run", response_model=GeneralStaticRunResponse)
def general_static_run(request: GeneralStaticRunRequest) -> GeneralStaticRunResponse:
    try:
        if request.terrain == "open":
            ce = calculate_open_terrain_exposure_factor(request.height)
        else:
            ce = calculate_rough_terrain_exposure_factor(request.height)

        cg = select_general_static_gust_effect_factor(
            request.code_edition,
            request.pressure_application,
        )

        cp_values = {
            "windward": calculate_windward_cp(
                request.height, request.wind_parallel_dimension
            ),
            "leeward": calculate_leeward_cp(
                request.height, request.wind_parallel_dimension
            ),
            "parallel_wall": calculate_parallel_wall_cp(),
            "roof": calculate_roof_cp(
                request.height, request.wind_parallel_dimension
            ),
        }

        surfaces = {}
        for name, cp in cp_values.items():
            pressure = calculate_general_static_pressure(
                importance_factor=request.importance_factor,
                reference_velocity_pressure=request.reference_velocity_pressure,
                exposure_factor=ce,
                topographic_factor=request.topographic_factor,
                gust_effect_factor=cg,
                pressure_coefficient=cp,
            )
            surfaces[name] = GeneralStaticSurfaceResult(cp=cp, pressure=pressure)

        return GeneralStaticRunResponse(
            exposure_factor=ce,
            gust_effect_factor=cg,
            **surfaces,
        )
    except (EngineeringInputError, UnsupportedEngineeringRuleError) as exc:
        raise _translate_engine_error(exc) from exc


@router.post(
    "/components-cladding/area-lookup",
    response_model=AreaLookupResponse,
)
def components_cladding_area_lookup(
    request: AreaLookupRequest,
) -> AreaLookupResponse:
    try:
        result = clamp_component_area_for_lookup(
            actual_area=request.actual_area,
            maximum_table_area=request.maximum_table_area,
        )
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc
    return AreaLookupResponse(
        actual_area=result.actual_area,
        lookup_area=result.lookup_area,
        maximum_table_area=result.maximum_table_area,
    )


@router.post(
    "/components-cladding/interpolate",
    response_model=InterpolationResponse,
)
def components_cladding_interpolate(
    request: InterpolationRequest,
) -> InterpolationResponse:
    try:
        coefficient = logarithmic_difference_interpolation(**request.model_dump())
    except EngineeringInputError as exc:
        raise _translate_engine_error(exc) from exc
    return InterpolationResponse(coefficient=coefficient)
