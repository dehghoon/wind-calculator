"""Engineering-specific exceptions.

Errors are intentionally explicit and are never silently corrected.
"""


class EngineeringCalculationError(Exception):
    """Base class for engineering calculation failures."""


class EngineeringInputError(EngineeringCalculationError, ValueError):
    """Raised when an engineering input violates an approved domain rule."""


class UnsupportedEngineeringRuleError(EngineeringCalculationError, NotImplementedError):
    """Raised when the approved specification does not contain enough data to calculate a rule."""
