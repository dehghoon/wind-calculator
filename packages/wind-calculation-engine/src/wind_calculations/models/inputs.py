"""Input data models."""

from dataclasses import dataclass

from ..validation.numeric import require_between, require_positive


@dataclass(frozen=True, slots=True)
class BuildingGeometry:
    """Building geometry in SI units.

    Parameters
    ----------
    height:
        Building height H, m.
    plan_dimension_b:
        Plan dimension B, m.
    plan_dimension_w:
        Plan dimension W, m.
    wind_parallel_dimension:
        Dimension D parallel to wind, m.
    roof_slope:
        Roof slope, degrees. Approved domain is 0 <= slope <= 90.
    """

    height: float
    plan_dimension_b: float
    plan_dimension_w: float
    wind_parallel_dimension: float
    roof_slope: float

    def __post_init__(self) -> None:
        require_positive("height", self.height, unit="m")
        require_positive("plan_dimension_b", self.plan_dimension_b, unit="m")
        require_positive("plan_dimension_w", self.plan_dimension_w, unit="m")
        require_positive("wind_parallel_dimension", self.wind_parallel_dimension, unit="m")
        require_between("roof_slope", self.roof_slope, minimum=0.0, maximum=90.0, unit="deg")

    @property
    def minimum_plan_dimension(self) -> float:
        """Return B_min = min(B, W), in m."""

        return min(self.plan_dimension_b, self.plan_dimension_w)
