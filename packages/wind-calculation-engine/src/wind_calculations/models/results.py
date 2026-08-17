"""Calculation result models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LowRiseApplicabilityResult:
    """Result of WIND-LR applicability evaluation."""

    applicable: bool
    height_limit_satisfied: bool
    aspect_ratio_limit_satisfied: bool
    minimum_plan_dimension: float
    height_to_minimum_plan_dimension_ratio: float


@dataclass(frozen=True, slots=True)
class LowRiseZoneDimensions:
    """NBC 2020 Low-Rise zone dimensions, in m."""

    z: float
    y: float


@dataclass(frozen=True, slots=True)
class AreaLookupResult:
    """Actual and clamped component areas, in m²."""

    actual_area: float
    lookup_area: float
    maximum_table_area: float
