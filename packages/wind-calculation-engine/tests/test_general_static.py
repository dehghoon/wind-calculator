import pytest

from wind_calculations import CodeEdition, PressureApplication
from wind_calculations.calculations.general_static import (
    calculate_general_static_pressure,
    calculate_leeward_cp,
    calculate_nbc2010_gust_effect_factor,
    calculate_nbc2020_gust_effect_factor,
    calculate_parallel_wall_cp,
    calculate_roof_cp,
    calculate_windward_cp,
    select_general_static_gust_effect_factor,
    select_general_static_topographic_factor,
)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (0.20, 0.6),
        (0.25, 0.27 * (0.25 + 2.0)),
        (0.75, 0.27 * (0.75 + 2.0)),
        (1.00, 0.8),
    ],
)
def test_f_gs_cp_01_all_branches(ratio, expected):
    assert calculate_windward_cp(ratio * 10.0, 10.0) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (0.20, -0.3),
        (0.25, -0.27 * (0.25 + 0.88)),
        (0.75, -0.27 * (0.75 + 0.88)),
        (1.00, -0.5),
    ],
)
def test_f_gs_cp_02_all_branches(ratio, expected):
    assert calculate_leeward_cp(ratio * 10.0, 10.0) == pytest.approx(expected)


def test_f_gs_cp_03_parallel_wall():
    assert calculate_parallel_wall_cp() == pytest.approx(-0.7)


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (1.10, -1.0),
        (0.25, -0.27 * (0.25 + 0.88)),
        (0.75, -0.27 * (0.75 + 0.88)),
        (1.00, -0.5),
        (0.20, -0.5),
    ],
)
def test_f_gs_cp_04_all_three_branches_and_strict_ratio_boundary(ratio, expected):
    assert calculate_roof_cp(ratio * 10.0, 10.0) == pytest.approx(expected)


@pytest.mark.parametrize(
    "calculator",
    [calculate_nbc2010_gust_effect_factor, calculate_nbc2020_gust_effect_factor],
)
def test_static_cg_values_match_both_editions(calculator):
    assert calculator(PressureApplication.BUILDING_AS_WHOLE) == 2.0
    assert calculator(PressureApplication.EXTERNAL_PRESSURE_SUCTION) == 2.5


def test_nbc2010_cg_selector_is_enabled():
    assert (
        select_general_static_gust_effect_factor(
            CodeEdition.NBC_2010,
            PressureApplication.BUILDING_AS_WHOLE,
        )
        == 2.0
    )


def test_topographic_factor_is_not_applied_to_nbc2010_static_equation():
    assert select_general_static_topographic_factor(CodeEdition.NBC_2010, 1.35) == 1.0


def test_topographic_factor_is_applied_to_nbc2020_static_equation():
    assert select_general_static_topographic_factor(CodeEdition.NBC_2020, 1.35) == pytest.approx(1.35)


def test_general_static_pressure_equation():
    assert calculate_general_static_pressure(1.0, 0.5, 1.1, 1.0, 2.0, -0.7) == pytest.approx(-0.77)
