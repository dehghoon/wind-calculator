"""Reusable numerical validation rules."""

import math
from numbers import Real

from ..exceptions import EngineeringInputError


def require_finite_number(name: str, value: float) -> float:
    """Validate that a value is a finite real number."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise EngineeringInputError(
            f"{name} must be a finite real number; received {type(value).__name__}. "
            "Provide a numeric engineering input."
        )
    numeric = float(value)
    if not math.isfinite(numeric):
        raise EngineeringInputError(
            f"{name} must be finite; received {value!r}. "
            "Provide a finite engineering input."
        )
    return numeric


def require_positive(name: str, value: float, *, unit: str = "") -> float:
    """Validate a strictly positive finite numeric input."""

    numeric = require_finite_number(name, value)
    if numeric <= 0.0:
        suffix = f" {unit}" if unit else ""
        raise EngineeringInputError(
            f"{name} must be > 0{suffix}; received {numeric}{suffix}. "
            "Provide a value inside the approved engineering domain."
        )
    return numeric


def require_between(
    name: str,
    value: float,
    *,
    minimum: float,
    maximum: float,
    unit: str = "",
) -> float:
    """Validate a finite value inside an inclusive range."""

    numeric = require_finite_number(name, value)
    if numeric < minimum or numeric > maximum:
        suffix = f" {unit}" if unit else ""
        raise EngineeringInputError(
            f"{name} must be between {minimum} and {maximum}{suffix}, inclusive; "
            f"received {numeric}{suffix}. Provide a value inside the approved engineering domain."
        )
    return numeric
