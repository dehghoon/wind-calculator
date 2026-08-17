"""WIND-GS General Static formula implementation."""

from ..enums import CodeEdition, PressureApplication
from ..exceptions import UnsupportedEngineeringRuleError
from ..validation.numeric import require_finite_number, require_positive


def _height_to_depth_ratio(height: float, depth: float) -> float:
    h = require_positive("height", height, unit="m")
    d = require_positive("wind_parallel_dimension", depth, unit="m")
    return h / d


def calculate_windward_cp(height: float, depth: float) -> float:
    """Calculate windward Cp.

    Formula ID
    ----------
    F-GS-CP-01

    Equation
    --------
    0.6 if H/D < 0.25
    0.27(H/D + 2) if 0.25 <= H/D < 1
    0.8 otherwise
    """

    ratio = _height_to_depth_ratio(height, depth)
    if ratio < 0.25:
        return 0.6
    if ratio < 1.0:
        return 0.27 * (ratio + 2.0)
    return 0.8


def calculate_leeward_cp(height: float, depth: float) -> float:
    """Calculate leeward Cp.

    Formula ID
    ----------
    F-GS-CP-02
    """

    ratio = _height_to_depth_ratio(height, depth)
    if ratio < 0.25:
        return -0.3
    if ratio < 1.0:
        return -0.27 * (ratio + 0.88)
    return -0.5


def calculate_parallel_wall_cp() -> float:
    """Calculate parallel-wall Cp.

    Formula ID
    ----------
    F-GS-CP-03
    """

    return -0.7


def calculate_roof_cp(height: float, depth: float) -> float:
    """Calculate approved project roof Cp.

    Formula ID
    ----------
    F-GS-CP-04

    Approved project logic
    ----------------------
    -1.0 if H/D > 1.0
    -0.27(H/D + 0.88) if 0.25 <= H/D < 1.0
    -0.5 otherwise

    Notes
    -----
    The strict first condition H/D > 1.0 is an approved user engineering
    decision modifying the source Mathcad condition and is preserved exactly.
    Therefore H/D == 1.0 falls into the final "otherwise" branch.
    """

    ratio = _height_to_depth_ratio(height, depth)
    if ratio > 1.0:
        return -1.0
    if 0.25 <= ratio < 1.0:
        return -0.27 * (ratio + 0.88)
    return -0.5


def calculate_nbc2020_gust_effect_factor(
    pressure_application: PressureApplication,
) -> float:
    """Return NBC 2020 project Cg selector from DEC-08.

    Building as a whole = 2.0.
    External pressure and suction = 2.5.
    """

    if pressure_application is PressureApplication.BUILDING_AS_WHOLE:
        return 2.0
    if pressure_application is PressureApplication.EXTERNAL_PRESSURE_SUCTION:
        return 2.5
    raise TypeError(
        "pressure_application must be a PressureApplication enum value."
    )


def select_general_static_gust_effect_factor(
    code_edition: CodeEdition,
    pressure_application: PressureApplication,
) -> float:
    """Select Cg without mixing code editions.

    NBC 2020 is implemented from DEC-08.
    NBC 2010 is intentionally unavailable because its exact edition-specific
    selector dataset/reference is unresolved in the supplied specification.
    """

    if code_edition is CodeEdition.NBC_2020:
        return calculate_nbc2020_gust_effect_factor(pressure_application)
    if code_edition is CodeEdition.NBC_2010:
        raise UnsupportedEngineeringRuleError(
            "NBC 2010 General Static Cg selection is not implemented because the approved "
            "specification does not provide the exact edition-specific selector data/reference. "
            "Supply the approved NBC 2010 rule dataset before enabling this calculation."
        )
    raise TypeError("code_edition must be a CodeEdition enum value.")


def calculate_general_static_pressure(
    importance_factor: float,
    reference_velocity_pressure: float,
    exposure_factor: float,
    topographic_factor: float,
    gust_effect_factor: float,
    pressure_coefficient: float,
) -> float:
    """Calculate General Static pressure.

    Equation
    --------
    p = Iw * q * Ce * Ct * Cg * Cp

    Returns
    -------
    float
        Pressure p, kPa when q is supplied in kPa.

    Notes
    -----
    Edition-specific selection of Iw, Ce, Ct and any unprovided coefficient
    dataset remains outside this formula function.
    """

    iw = require_positive("importance_factor", importance_factor)
    q = require_positive("reference_velocity_pressure", reference_velocity_pressure, unit="kPa")
    ce = require_positive("exposure_factor", exposure_factor)
    ct = require_positive("topographic_factor", topographic_factor)
    cg = require_positive("gust_effect_factor", gust_effect_factor)
    cp = require_finite_number("pressure_coefficient", pressure_coefficient)
    return iw * q * ce * ct * cg * cp
