import pytest

from wind_calculations import BuildingGeometry
from wind_calculations.calculations.low_rise import (
    calculate_low_rise_external_pressure,
    calculate_nbc2020_low_rise_zone_dimensions,
    calculate_open_terrain_exposure_factor,
    calculate_rough_terrain_exposure_factor,
    is_low_rise_applicable,
)
from wind_calculations.exceptions import EngineeringInputError


def geometry(*, h: float, b: float, w: float) -> BuildingGeometry:
    return BuildingGeometry(
        height=h,
        plan_dimension_b=b,
        plan_dimension_w=w,
        wind_parallel_dimension=30.0,
        roof_slope=7.0,
    )


def test_low_rise_height_boundary_20m_is_accepted_when_ratio_is_below_one():
    result = is_low_rise_applicable(geometry(h=20.0, b=25.0, w=30.0))
    assert result.applicable is True


def test_low_rise_ratio_boundary_one_is_rejected():
    result = is_low_rise_applicable(geometry(h=20.0, b=20.0, w=30.0))
    assert result.applicable is False
    assert result.aspect_ratio_limit_satisfied is False


def test_roof_slope_90_is_accepted():
    BuildingGeometry(10.0, 20.0, 25.0, 20.0, 90.0)


def test_roof_slope_above_90_is_rejected():
    with pytest.raises(EngineeringInputError):
        BuildingGeometry(10.0, 20.0, 25.0, 20.0, 90.0001)


def test_open_terrain_exposure_factor_formula():
    assert calculate_open_terrain_exposure_factor(10.0) == pytest.approx(1.0)


def test_rough_terrain_exposure_factor_formula():
    assert calculate_rough_terrain_exposure_factor(12.0) == pytest.approx(0.7)


def test_nbc2020_zone_dimensions_formula():
    result = calculate_nbc2020_low_rise_zone_dimensions(geometry(h=10.0, b=20.0, w=30.0))
    assert result.z == pytest.approx(2.0)
    assert result.y == pytest.approx(6.0)


def test_low_rise_pressure_retains_ch():
    result = calculate_low_rise_external_pressure(
        importance_factor=1.0,
        reference_velocity_pressure=0.5,
        exposure_factor=1.0,
        gust_pressure_coefficient=-1.2,
        height_factor=0.8,
    )
    assert result == pytest.approx(-0.48)
