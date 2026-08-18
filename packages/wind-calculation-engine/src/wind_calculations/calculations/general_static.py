"""WIND-GS General Static formula implementation."""

from ..enums import CodeEdition, PressureApplication
from ..validation.numeric import require_finite_number, require_positive


def _height_to_depth_ratio(height: float, depth: float) -> float:
    h = require_positive("height", height, unit="m")
    d = require_positive("wind_parallel_dimension", depth, unit="m")
    return h / d


def calculate_windward_cp(height: float, depth: float) -> float:
    """Calculate windward Cp."""
    ratio = _height_to_depth_ratio(height, depth)
    if ratio < 0.25:
        return 0.6
    if ratio < 1.0:
        return 0.27 * (ratio + 2.0)
    return 0.8


def calculate_leeward_cp(height: float, depth: float) -> float:
    """Calculate leeward Cp."""
    ratio = _height_to_depth_ratio(height, depth)
    if ratio < 0.25:
        return -0.3
    if ratio < 1.0:
        return -0.27 * (ratio + 0.88)
    return -0.5


def calculate_parallel_wall_cp() -> float:
    """Calculate parallel-wall Cp."""
    return -0.7


def calculate_roof_cp(height: float, depth: float) -> float:
    """Calculate approved project roof Cp.

    This preserves the current project-approved roof logic. The supplied NBCC 2010
    excerpt does not include Article 4.1.7.5 roof-Cp provisions, so this function is
    not claimed as a newly verified 2010 extraction.
    """
    ratio = _height_to_depth_ratio(height, depth)
    if ratio > 1.0:
        return -1.0
    if 0.25 <= ratio < 1.0:
        return -0.27 * (ratio + 0.88)
    return -0.5


def _static_gust_effect_factor(
    pressure_application: PressureApplication,
) -> float:
    """Return the static-procedure Cg used by both NBCC 2010 and NBCC 2020.

    NBCC 2010 Article 4.1.7.1 Sentence (6):
      * building as a whole / main structural members = 2.0
      * external pressures and suctions on small elements including cladding = 2.5

    NBCC 2020 Article 4.1.7.3 Sentence (8) retains the same two values.
    """
    if pressure_application is PressureApplication.BUILDING_AS_WHOLE:
        return 2.0
    if pressure_application is PressureApplication.EXTERNAL_PRESSURE_SUCTION:
        return 2.5
    raise TypeError("pressure_application must be a PressureApplication enum value.")


def calculate_nbc2010_gust_effect_factor(
    pressure_application: PressureApplication,
) -> float:
    return _static_gust_effect_factor(pressure_application)


def calculate_nbc2020_gust_effect_factor(
    pressure_application: PressureApplication,
) -> float:
    return _static_gust_effect_factor(pressure_application)


def select_general_static_gust_effect_factor(
    code_edition: CodeEdition,
    pressure_application: PressureApplication,
) -> float:
    """Select edition-specific static-procedure Cg."""
    if code_edition is CodeEdition.NBC_2010:
        return calculate_nbc2010_gust_effect_factor(pressure_application)
    if code_edition is CodeEdition.NBC_2020:
        return calculate_nbc2020_gust_effect_factor(pressure_application)
    raise TypeError("code_edition must be a CodeEdition enum value.")


def select_general_static_topographic_factor(
    code_edition: CodeEdition,
    supplied_topographic_factor: float,
) -> float:
    """Return the edition-appropriate factor applied in the static pressure equation.

    The supplied NBCC 2010 Article 4.1.7.1 external-pressure equation is
    p = Iw*q*Ce*Cg*Cp and contains no Ct term, so the engine uses an effective
    factor of 1.0 for 2010. NBCC 2020 Article 4.1.7.3 includes Ct explicitly.
    """
    if code_edition is CodeEdition.NBC_2010:
        return 1.0
    if code_edition is CodeEdition.NBC_2020:
        return require_positive(
            "topographic_factor", supplied_topographic_factor
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

    The caller supplies an edition-selected effective topographic factor:
    1.0 for NBCC 2010, and Ct for NBCC 2020.
    """
    iw = require_positive("importance_factor", importance_factor)
    q = require_positive(
        "reference_velocity_pressure", reference_velocity_pressure, unit="kPa"
    )
    ce = require_positive("exposure_factor", exposure_factor)
    ct = require_positive("topographic_factor", topographic_factor)
    cg = require_positive("gust_effect_factor", gust_effect_factor)
    cp = require_finite_number("pressure_coefficient", pressure_coefficient)
    return iw * q * ce * ct * cg * cp
