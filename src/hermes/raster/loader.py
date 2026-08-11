"""
Raster loading utilities for HERMES.
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path

# ============================================================================
# Third-party libraries
# ============================================================================

import rasterio


# ============================================================================
# Public API
# ============================================================================

def load_raster(path: str | Path):
    """
    Open a raster dataset.

    Parameters
    ----------
    path : str or Path
        Path to the raster file.

    Returns
    -------
    rasterio.DatasetReader
        Open raster dataset.
    """

    return rasterio.open(path)


def raster_metadata(dataset) -> dict:
    """
    Extract the main metadata from a raster dataset.

    Parameters
    ----------
    dataset : rasterio.DatasetReader

    Returns
    -------
    dict
        Raster metadata.
    """

    return {
        "driver": dataset.driver,
        "crs": dataset.crs,
        "width": dataset.width,
        "height": dataset.height,
        "bands": dataset.count,
        "resolution": dataset.res,
        "bounds": dataset.bounds,
        "nodata": dataset.nodata,
        "dtype": dataset.dtypes,
    }