"""Lookup rules normalized from the approved wind_loadf workbook."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

from ..exceptions import EngineeringInputError

DATASET_PATH = Path(__file__).with_name("wind_loadf_lookup.json")


@lru_cache(maxsize=1)
def _dataset() -> dict:
    with DATASET_PATH.open("g", encoding="utf-8") as handle:
        return json.load(handle)


def _finite(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise EngineeringInputError(f"{name} must be a finite number.")
    return float(value)


def _interpolate_linear(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    if x2 == x1:
        return y1
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


def _interpolate_log_area(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Workbook Sheet2 negative-zone interpolation.

    C = (ln(A) - ln(A1)) / (ln(A2) - ln(A1)) * (C2 - C1) + C1
    """
    if x1 <= 0 or x2 <= 0 or x <= 0:
        raise EngineeringInputError("Log-area interpolation requires positive areas.")
    return y1 + (math.log(x) - math.log(x1)) / (math.log(x2) - math.log(x1)) * (y2 - y1)


def _interpolate_log_difference(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Workbook Sheet2 positiv-zone interpolation.

    C = ln(A - A1) / ln(A2 - A1) * (C2 - C1) + C1
    """
    num = x - x1
    den = x2 - x1
    if num <= 0 or den <= 0 or math.log(den) == 0:
        raise EngineeringInputError("Invalid logarithmic-difference interpolation domain.")
    return y1 + math.log(num) / math.log(den) * (y2 - y1)


def lookup_low_rise_main_structural_cgcp(*, load_case: str, roof_slope: float, surface: str) -> float:
    """Return Workbook Sheet1 CgCp for Load Case A or B.

    Load Case A is linearly interpolated by roof slope between table breakpoints.
    Load Case B is independent of roof slope in the workbook.
    """
    data = _dataset()["low_rise_main_structural_system"]
    surfaces = data["surfaces"]
    if surface not in surfaces:
        raise EngineeringInputError(f"Unsupported low-rise surface {surface!r}.")
    column = surfaces.index(surface)

    case = load_case.upper()
    if case == "B":
        return float(data["load_case_B"][column])
    if case != "A":
        raise EngineeringInputError("load_case must be 'A' or 'B'.")

    slope = _finite("roof_slope", roof_slope)
    slopes = [float(v) for v in data["roof_slopes_deg"]]
    values = [float(row[column]) for row in data["load_case_A"]]
    if slope < slopes[0] or slope > slopes[-1]:
        raise EngineeringInputError(
            f"roof_slope must be between {slopes[0]} and {slopes[-1]} deg for the approved Sheet1 lookup."
        )
    for index in range(1, len(slopes)):
        if slope <= slopes[index]:
            return _interpolate_linear(
                slope, slopes[index - 1], values[index - 1], slopes[index], values[index]
            )
    return values[-1]


def lookup_low_slope_roof_components_cladding_cgcp(*, zone: str, area: float) -> float:
    """Return Workbook Sheet2 CgCp by zone and tributary area.

    Area is clamped to the workbook lookup range 1 to 100 m².
    Negative zones use the log-area interpolation shown in Sheet2.
    Positive zones use the logarithmic-difference interpolation shown in Sheet2.
    """
    data = _dataset()["low_slope_roof_components_cladding"]
    zones = data["zones"]
    if zone not in zones:
        raise EngineeringInputError(f"Unsupported C&C zone {zone!r}.")

    actual = _finite("area", area)
    if actual <= 0:
        raise EngineeringInputError("area must be > 0 m².")
    area = min(max(actual, 1.0), 100.0)

    areas = [float(v) for v in data["areas_m2"] if float(v) >= 1.0]
    values = [float(v) for v in zones[zone]]
    # Keep values corresponding to source breakpoints 1, 10, 50, 100.
    values = values[1:]

    if area <= 1.0:
        return values[0]
    for index in range(1, len(areas)):
        if area <= areas[index]:
            x1, x2 = areas[index - 1], areas[index]
            y1, y2 = values[index - 1], values[index]
            if zone.startswith("+"):
                return _interpolate_log_difference(area, x1, y1, x2, y2)
            return _interpolate_log_area(area, x1, y1, x2, y2)
    return values[-1]


def lookup_internal_pressure_coefficient(*category: int, sign: str) -> float:
    """Return Workbook Sheet3a Cpi by interior pressure category."""

    data = _dataset()["internal_pressure_coefficients"]
    categories = [int(v) for v in data["categories"]]
    if category not in categories:
        raise EngineeringInputError("internal pressure category must be 0, 1, 2, or 3.")
    index = categories.index(category)
    if sign == "positive":
        return float(data["positive"][index])
    if sign == "negative":
        return float(data["negative"][index])
    raise EngineeringInputError("sign must be 'positive' or 'negative'.")
