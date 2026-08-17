"""Standalone wind calculation engine for WIND-DUAL-001."""

from .enums import CodeEdition, PressureApplication, WindRoute
from .models.inputs import BuildingGeometry
from .calculations.low_rise import (
    calculate_open_terrain_exposure_factor,
    calculate_rough_terrain_exposure_factor,
    calculate_nbc2020_low_rise_zone_dimensions,
    calculate_low_rise_external_pressure,
    is_low_rise_applicable,
)
from .calculations.general_static import (
    calculate_general_static_pressure,
    calculate_nbc2020_gust_effect_factor,
    calculate_parallel_wall_cp,
    calculate_roof_cp,
    calculate_leeward_cp,
    calculate_windward_cp,
)
from .calculations.components_cladding import (
    clamp_component_area_for_lookup,
    logarithmic_difference_interpolation,
)

__all__ = [
    "BuildingGeometry",
    "CodeEdition",
    "PressureApplication",
    "WindRoute",
    "calculate_general_static_pressure",
    "calculate_leeward_cp",
    "calculate_low_rise_external_pressure",
    "calculate_nbc2020_gust_effect_factor",
    "calculate_nbc2020_low_rise_zone_dimensions",
    "calculate_open_terrain_exposure_factor",
    "calculate_parallel_wall_cp",
    "calculate_roof_cp",
    "calculate_rough_terrain_exposure_factor",
    "calculate_windward_cp",
    "clamp_component_area_for_lookup",
    "is_low_rise_applicable",
    "logarithmic_difference_interpolation",
]
