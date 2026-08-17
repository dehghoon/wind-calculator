import math
import pytest

from wind_calculations.exceptions import EngineeringInputError
from wind_calculations.validation.numeric import require_finite_number, require_positive


@pytest.mark.parametrize("value", [0.0, -1.0])
def test_positive_input_rejects_nonpositive_values(value):
    with pytest.raises(EngineeringInputError):
        require_positive("dimension", value, unit="m")


@pytest.mark.parametrize("value", [math.inf, -math.inf, math.nan])
def test_finite_input_rejects_nonfinite_values(value):
    with pytest.raises(EngineeringInputError):
        require_finite_number("value", value)


def test_bool_is_not_accepted_as_engineering_number():
    with pytest.raises(EngineeringInputError):
        require_finite_number("value", True)
