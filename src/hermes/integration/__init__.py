"""
Integration utilities for HERMES.
"""

from .municipality import build_municipality_table
from .population import integrate_population
from .employment import integrate_employment
from .workplace_employment import integrate_workplace_employment

__all__ = [
    "build_municipality_table",
    "integrate_population",
    "integrate_employment",
    "integrate_workplace_employment",
]
