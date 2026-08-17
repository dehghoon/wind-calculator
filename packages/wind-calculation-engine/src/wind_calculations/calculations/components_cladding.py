"""WIND-CC Components & Cladding helper calculations."""

import math

from ..exceptions import EngineeringInputError
from ..models.results import AreaLookupResult
from ..validation.numeric import require_finite_number, require_positive


def clamp_component_area_for_lookup(
    actual_area: float,
    maximum_table_area: float,
) -> AreaLookupResult:
    """Clamp component area for coefficient lookup while retaining actual area.

    Approved rule
    -------------
    A_lookup = 1 m² if A_actual < 1
    A_lookup = A_actual if 1 <= A_actual <= Amax
    A_lookup = Amax if A_actual > Amax

    DEC-02 and DEC-07 are preserved: component area is a user input and must not
    be replaced by B x W.
    """

    actual = require_positive("actual_area", actual_area, unit="m²")
    maximum = require_positive("maximum_table_area", maximum_table_area, unit="m²")
    if maximum < 1.0:
        raise EngineeringInputError(
            "maximum_table_area must be >= 1 m² because the approved lookup rule "
            "uses 1 m² as its lower lookup bound."
        )
    lookup = min(max(actual, 1.0), maximum)
    return AreaLookupResult(
        actual_area=actual,
        lookup_area=lookup,
        maximum_table_area=maximum,
    )


def logarithmic_difference_interpolation(
    area: float,
    area_1: float,
    coefficient_1: float,
    area_2: float,
    coefficient_2: float,
) -> float:
    """Apply approved positive +S/+R/+C interpolation.

    Equation
    --------
    C = C1 + (C2 - C1) * ln(A - A1) / ln(A2 - A1)

    Important
    ---------
    This is a project method from DEC-06. The source specification explicitly
    says not to label it as an explicit NBC equation.

    Domain
    ------
    The logarithm arguments must be strictly positive and the denominator must
    be non-zero. No extrapolation or silent adjustment is performed.
    """

    a = require_finite_number("area", area)
    a1 = require_finite_number("area_1", area_1)
    a2 = require_finite_number("area_2", area_2)
    c1 = require_finite_number("coefficient_1", coefficient_1)
    c2 = require_finite_number("coefficient_2", coefficient_2)

    numerator_argument = a - a1
    denominator_argument = a2 - a1
    if numerator_argument <= 0.0:
        raise EngineeringInputError(
            "area - area_1 must be > 0 for the approved logarithmic-difference interpolation; "
            f"received area={a}, area_1={a1}."
        )
    if denominator_argument <= 0.0:
        raise EngineeringInputError(
            "area_2 - area_1 must be > 0 for the approved logarithmic-difference interpolation; "
            f"received area_2={a2}, area_1={a1}."
        )

    denominator = math.log(denominator_argument)
    if denominator == 0.0:
        raise EngineeringInputError(
            "ln(area_2 - area_1) is zero, causing division by zero in the approved "
            "interpolation equation. Choose approved bracket values with area_2 - area_1 != 1."
        )

    return c1 + (c2 - c1) * math.log(numerator_argument) / denominator
