"""
Raster metadata utilities.
"""

from rasterio.io import DatasetReader


def raster_metadata(
    dataset: DatasetReader,
) -> dict:
    """
    Extract the main metadata from a raster dataset.
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