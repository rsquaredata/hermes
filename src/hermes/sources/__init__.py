"""
Data source download utilities.
"""

from .ign import download_municipality_boundaries

from .insee import (
    download_population,
    download_employment,
    download_workplace_employment,
    download_mobility,
)

from .topography import download_topography

from .climate import download_climate

__all__ = [
    "download_population",
    "download_employment",
    "download_workplace_employment",
    "download_mobility",
    "download_municipality_boundaries",
    "download_topography",
    "download_climate",
]