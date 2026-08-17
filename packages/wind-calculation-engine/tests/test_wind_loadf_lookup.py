import pytest

from wind_calculations.datasets.wind_loadf import (
    lookup_internal_pressure_coefficient,
    lookup_low_rise_main_structural_cgcp,
    lookup_low_slope_roof_components_cladding_cgcp,
)


def test_sheet1_exact_load_case_a_breakpoint() -> None:
    assert lookup_low_rise_main_structural_cgcp(
        load_case="A", roof_slope=20.0, surface="1E"
    ) == pytest.approx(1.5)


def test_sheet1_linear_slope_interpolation() -> None:
    assert lookup_low_rise_main_structural_cgcp(
        load_case="A", roof_slope=25.0, surface="1"
    ) == pytest.approx(1.025)


def test_sheet1_load_case_b_is_slope_independent() -> None:
    assert lookup_low_rise_main_structural_cgcp(
        load_case="B", roof_slope=37.0, surface="5E"
    ) == pytest.approx(1.15)


def test_sheet2_negative_zone_log_area_interpolation() -> None:
    assert lookup_low_slope_roof_components_cladding_cgcp(
        zone="-C", area=7.095337742966286
   ) == pytest.approx(-2.5066915517926667)


def test_sheet2_positive_zone_difference_log_interpolation() -> None:
    assert lookup_low_slope_roof_components_cladding_cgcp(
        zone="+S", area=7.095337742966286
   ) == pytest.approx(0.33547205932774543)


def test_sheet2_lookup_area_bounds_are_compatible() -> None:
    assert lookup_low_slope_roof_components_cladding_cgcp(
        zone="-C", area=0.2
    ) == pytest.approx(-5.4)
    assert lookup_low_slope_roof_components_cladding_cgcp(
        zone="-C", area=250.0
    ) == pytest.approx(-2.0)


def test_sheet3a_internal_pressure_lookup() -> None:
    assert lookup_internal_pressure_coefficient(category=3, sign="positive") == pytest.approx(0.7)
    assert lookup_internal_pressure_coefficient(category=3, sign="negative") == pytest.approx(-0.7)
