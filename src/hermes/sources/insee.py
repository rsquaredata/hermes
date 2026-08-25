"""
INSEE data sources for HERMES.
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path

# ============================================================================
# Local imports
# ============================================================================

from hermes.data_catalog import get_dataset
from hermes.io import download_file


# ============================================================================
# Internal helper
# ============================================================================

def _download_dataset(
    dataset_name: str,
    overwrite: bool = False,
) -> Path:
    """
    Download a dataset defined in the data catalog.
    """

    dataset = get_dataset(dataset_name)

    return download_file(
        url=dataset.url,
        destination=dataset.download_path,
        overwrite=overwrite,
    )


# ============================================================================
# Public API
# ============================================================================

def download_population(overwrite: bool = False) -> Path:
    return _download_dataset("population", overwrite)


def download_employment(overwrite: bool = False) -> Path:
    return _download_dataset("employment", overwrite)


def download_workplace_employment(overwrite: bool = False) -> Path:
    return _download_dataset("workplace_employment", overwrite)


def download_mobility(overwrite: bool = False) -> Path:
    return _download_dataset("mobility", overwrite)