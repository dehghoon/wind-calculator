import math
import pytest

from wind_calculations.calculations.components_cladding import (
    clamp_component_area_for_lookup,
    logarithmic_difference_interpolation,
)
from wind_calculations.exceptions import EngineeringInputError


def test_area_below_1_uses_1_for_lookup_and_retains_actual():
    result = clamp_component_area_for_lookup(0.4, 50.0)
    assert result.actual_area == pytest.approx(0.4)
    assert result.lookup_area == pytest.approx(1.0)


def test_area_inside_range_is_retained():
    result = clamp_component_area_for_lookup(5.0, 50.0)
    assert result.lookup_area == pytest.approx(5.0)


def test_area_above_maximum_uses_maximum_without_extrapolation():
    result = clamp_component_area_for_lookup(80.0, 50.0)
    assert result.actual_area == pytest.approx(80.0)
    assert result.lookup_area == pytest.approx(50.0)


def test_logarithmic_difference_interpolation_matches_approved_equation():
    actual = logarithmic_difference_interpolation(3.0, 1.0, -1.0, 5.0, -2.0)
    expected = -1.0 + (-1.0) * math.log(2.0) / math.log(4.0)
    assert actual == pytest.approx(expected)


def test_logarithmic_difference_interpolation_rejects_invalid_log_domain():
    with pytest.raises(EngineeringInputError):
        logarithmic_difference_interpolation(1.0, 1.0, -1.0, 5.0, -2.0)
