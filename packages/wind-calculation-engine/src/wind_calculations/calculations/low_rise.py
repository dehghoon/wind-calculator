"""WIND-LR Low-Rise formula implementation.

Only formulas explicitly present in WIND-DUAL-001 are implemented here.
Edition-specific coefficient tables not supplied by the approved specification
are intentionally not invented.
"""

from ..models.inputs import BuildingGeometry
from ..models.results import LowRiseApplicabilityResult, LowRiseZoneDimensions
from ..validation.numeric import require_finite_number, require_positive


def is_low_rise_applicable(geometry: BuildingGeometry) -> LowRiseApplicabilityResult:
    """Evaluate WIND-LR applicability.

    Formula
    -------
    H <= 20 m AND H / B_min < 1, where B_min = min(B, W).

    Specification traceability
    --------------------------
    Route: WIND-LR, Section 4, Low-Rise applicability.

    Returns
    -------
    LowRiseApplicabilityResult
        Detailed applicability status.

    Notes
    -----
    The H = 20 m boundary is accepted. The H/B_min = 1 boundary is not.
    """

    b_min = geometry.minimum_plan_dimension
    ratio = geometry.height / b_min
    height_ok = geometry.height <= 20.0
    ratio_ok = ratio < 1.0
    return LowRiseApplicabilityResult(
        applicable=height_ok and ratio_ok,
        height_limit_satisfied=height_ok,
        aspect_ratio_limit_satisfied=ratio_ok,
        minimum_plan_dimension=b_min,
        height_to_minimum_plan_dimension_ratio=ratio,
    )


def calculate_open_terrain_exposure_factor(height: float) -> float:
    """Calculate approved open-terrain exposure factor Ce.

    Equation
    --------
    Ce_open = max(0.9, (h / 10)^0.2)

    Parameters
    ----------
    height:
        Height h, m.

    Returns
    -------
    float
        Dimensionless Ce.
    """

    h = require_positive("height", height, unit="m")
    return max(0.9, (h / 10.0) ** 0.2)


def calculate_rough_terrain_exposure_factor(height: float) -> float:
    """Calculate approved rough-terrain exposure factor Ce.

    Equation
    --------
    Ce_rough = max(0.7, 0.7(h / 12)^0.3)

    Parameters
    ----------
    height:
        Height h, m.

    Returns
    -------
    float
        Dimensionless Ce.
    """

    h = require_positive("height", height, unit="m")
    return max(0.7, 0.7 * (h / 12.0) ** 0.3)


def calculate_nbc2020_low_rise_zone_dimensions(
    geometry: BuildingGeometry,
) -> LowRiseZoneDimensions:
    """Calculate NBC 2020 Low-Rise zone dimensions z and y.

    Equations
    ---------
    z = max(min(0.10 B_min, 0.40 H), 0.04 B_min, 1 m)
    y = max(6 m, 2z)

    Returns
    -------
    LowRiseZoneDimensions
        z and y in metres.
    """

    b_min = geometry.minimum_plan_dimension
    h = geometry.height
    z = max(min(0.10 * b_min, 0.40 * h), 0.04 * b_min, 1.0)
    y = max(6.0, 2.0 * z)
    return LowRiseZoneDimensions(z=z, y=y)


def calculate_low_rise_external_pressure(
    importance_factor: float,
    reference_velocity_pressure: float,
    exposure_factor: float,
    gust_pressure_coefficient: float,
    height_factor: float,
) -> float:
    """Calculate WIND-LR external pressure.

    Equation
    --------
    p_ext = Iw * q * Ce * (CgCp) * Ch

    Parameters
    ----------
    importance_factor:
        Iw, dimensionless. Selection/mapping from importance category is not
        included because the edition-specific dataset is absent from the supplied specification.
    reference_velocity_pressure:
        q, kPa.
    exposure_factor:
        Ce, dimensionless.
    gust_pressure_coefficient:
        CgCp, dimensionless. Must be selected from an approved edition-specific dataset.
    height_factor:
        Ch, dimensionless project engineering parameter retained by DEC-03.

    Returns
    -------
    float
        External pressure p_ext, kPa.

    Notes
    -----
    This function implements only the stated pressure equation. It does not
    select Iw, CgCp, or Ch from missing source datasets.
    """

    iw = require_positive("importance_factor", importance_factor)
    q = require_positive("reference_velocity_pressure", reference_velocity_pressure, unit="kPa")
    ce = require_positive("exposure_factor", exposure_factor)
    cgcp = require_finite_number("gust_pressure_coefficient", gust_pressure_coefficient)
    ch = require_positive("height_factor", height_factor)
    return iw * q * ce * cgcp * ch
