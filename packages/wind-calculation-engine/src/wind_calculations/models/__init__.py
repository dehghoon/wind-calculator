"""Data models for wind calculations."""

from .inputs import BuildingGeometry
from .results import (
    AreaLookupResult,
    LowRiseApplicabilityResult,
    LowRiseZoneDimensions,
)

__all__ = [
    "AreaLookupResult",
    "BuildingGeometry",
    "LowRiseApplicabilityResult",
    "LowRiseZoneDimensions",
]
