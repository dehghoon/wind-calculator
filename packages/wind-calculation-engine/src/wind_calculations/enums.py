"""Enumerations used by the wind calculation engine."""

from enum import Enum


class CodeEdition(str, Enum):
    """Supported NBC editions."""

    NBC_2010 = "NBC_2010"
    NBC_2020 = "NBC_2020"


class WindRoute(str, Enum):
    """Calculation routes defined by WIND-DUAL-001."""

    LOW_RISE = "WIND-LR"
    GENERAL_STATIC = "WIND-GS"
    COMPONENTS_CLADDING = "WIND-CC"


class PressureApplication(str, Enum):
    """General Static gust effect factor selection."""

    BUILDING_AS_WHOLE = "building_as_whole"
    EXTERNAL_PRESSURE_SUCTION = "external_pressure_and_suction"
