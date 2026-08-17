"""Minimal typed report-content models from the report specification."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..enums import CodeEdition, WindRoute


@dataclass(frozen=True, slots=True)
class ReportMetadata:
    calculation_id: str
    route: WindRoute
    revision: str
    generated_at: datetime
    code_edition: CodeEdition
    unit_system: str = "SI"
    project_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CalculationStep:
    step_id: str
    formula_id: str
    title: str
    equation: str
    substitutions: dict[str, Any]
    dependencies: tuple[str, ...]
    result: float
    unit: str
    reference_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResultItem:
    output_id: str
    description: str
    raw_value: float
    display_value: str
    unit: str
    governing_case: str | None = None
    status: str | None = None


@dataclass(frozen=True, slots=True)
class EngineeringWarning:
    warning_id: str
    severity: str
    message: str
    affected_items: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EngineeringReference:
    reference_id: str
    standard: str
    edition: str
    article_clause: str | None
    table_figure: str | None
    application: str
    verification_status: str


@dataclass(frozen=True, slots=True)
class ValidationStatement:
    benchmark_id: str
    expected_results: dict[str, float]
    tolerance: float
    status: str
