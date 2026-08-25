"""
Elevation processing utilities for HERMES.

This module provides functions for working with digital elevation models,
with a focus on IGN RGE ALTI data.

It includes utilities for:

- identifying RGE ALTI tiles
- locating tiles from Lambert-93 coordinates
- computing terrain slope
- resampling elevation rasters
- comparing slope statistics across spatial resolutions
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path
import re

# ============================================================================
# Third-party libraries
# ============================================================================

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.features import geometry_mask
from rasterio.merge import merge
from shapely.geometry import box, mapping

# ============================================================================
# Local imports
# ============================================================================

from hermes.utils import (
    extract_7z_files,
    list_7z,
)


# ============================================================================
# RGE ALTI tile utilities
# ============================================================================

def build_tile_grid(
    geometry,
    crs: str = "EPSG:2154",
    tile_size: int = 1_000,
    buffer: float = 0,
) -> gpd.GeoDataFrame:
    """
    Build the RGE ALTI kilometre grid intersecting a geometry.

    An optional spatial buffer can be applied before selecting tiles.
    This is useful when neighbouring elevation data are required for
    raster resampling or terrain-gradient calculations.

    Parameters
    ----------
    geometry
        Study-area geometry in Lambert-93 coordinates.

    crs
        Coordinate reference system of the geometry.

    tile_size
        Tile size in metres.

    buffer
        Buffer applied around the geometry before selecting tiles,
        in metres.

    Returns
    -------
    geopandas.GeoDataFrame
        RGE ALTI tiles intersecting the buffered study area.
    """

    if isinstance(
        geometry,
        (gpd.GeoDataFrame, gpd.GeoSeries),
    ):
        geometry = geometry.geometry.union_all()

    selection_geometry = geometry.buffer(
        buffer
    )

    minx, miny, maxx, maxy = (
        selection_geometry.bounds
    )

    grid_minx = (
        np.floor(minx / tile_size)
        * tile_size
    )

    grid_miny = (
        np.floor(miny / tile_size)
        * tile_size
    )

    grid_maxx = (
        np.ceil(maxx / tile_size)
        * tile_size
    )

    grid_maxy = (
        np.ceil(maxy / tile_size)
        * tile_size
    )

    tiles = []

    for x in np.arange(
        grid_minx,
        grid_maxx,
        tile_size,
    ):
        for y in np.arange(
            grid_miny,
            grid_maxy,
            tile_size,
        ):
            tile = box(
                x,
                y,
                x + tile_size,
                y + tile_size,
            )

            if tile.intersects(
                selection_geometry
            ):
                tiles.append(
                    {
                        "tile_x": int(x),
                        "tile_y": int(y),
                        "ign_tile_id": (
                            f"{int(x // 1000):04d}_"
                            f"{int((y + tile_size) // 1000):04d}"
                        ),
                        "geometry": tile,
                    }
                )

    return gpd.GeoDataFrame(
        tiles,
        geometry="geometry",
        crs=crs,
    )


def build_mnt_index(
    files: list[str],
) -> dict[str, str]:
    """
    Build an index of RGE ALTI MNT files by IGN tile identifier.

    Parameters
    ----------
    files
        File paths contained in an RGE ALTI archive.

    Returns
    -------
    dict[str, str]
        Mapping between IGN tile identifiers and archive paths.
    """

    pattern = re.compile(
        r"RGEALTI_FXX_"
        r"(\d{4})_(\d{4})_"
        r"MNT_LAMB93_IGN69\.asc$"
    )

    index = {}

    for path in files:

        match = pattern.search(
            path
        )

        if match is None:
            continue

        tile_id = (
            f"{match.group(1)}_"
            f"{match.group(2)}"
        )

        index[tile_id] = path

    return index


def get_tile_coordinates(
    path: str | Path,
) -> tuple[int, int]:
    """
    Extract Lambert-93 kilometre tile coordinates
    from an RGE ALTI filename.

    Parameters
    ----------
    path
        Path to an RGE ALTI MNT tile.

    Returns
    -------
    tuple[int, int]
        Tile coordinates expressed in kilometres.
    """

    path = Path(path)

    match = re.search(
        r"FXX_(\d{4})_(\d{4})_MNT",
        path.name,
    )

    if match is None:
        raise ValueError(
            f"Cannot parse tile coordinates: {path.name}"
        )

    return (
        int(match.group(1)),
        int(match.group(2)),
    )


def find_tile_for_point(
    mnt_files: list[Path],
    x: float,
    y: float,
) -> Path:
    """
    Find the RGE ALTI tile containing a Lambert-93 point.

    Parameters
    ----------
    mnt_files
        Available RGE ALTI MNT files.

    x
        Lambert-93 easting in metres.

    y
        Lambert-93 northing in metres.

    Returns
    -------
    Path
        Path to the corresponding MNT tile.
    """

    x_km = int(x // 1000)
    y_km = int(y // 1000)

    for path in mnt_files:

        tile_x, tile_y = get_tile_coordinates(
            path
        )

        if (
            tile_x == x_km
            and tile_y == y_km
        ):
            return Path(path)

    raise FileNotFoundError(
        f"No RGE ALTI tile found for point ({x}, {y})."
    )


def prepare_case_study_mnt(
    selected_tiles: gpd.GeoDataFrame,
    rhone_archive: str | Path,
    ain_archive: str | Path,
    destination: str | Path,
    optional_tile_ids: set[str] | None = None,
) -> list[Path]:
    """
    Prepare RGE ALTI MNT tiles for the HERMES case-study area.

    The function identifies the required IGN tiles, matches them
    against the Rhône and Ain RGE ALTI archives, extracts only the
    necessary MNT files, and validates the resulting coverage.

    Existing extracted tiles are reused.

    Parameters
    ----------
    selected_tiles
        RGE ALTI kilometre tiles intersecting the case-study area.
        Must contain an ``ign_tile_id`` column.

    rhone_archive
        Path to the Rhône RGE ALTI archive.

    ain_archive
        Path to the Ain RGE ALTI archive.

    destination
        Directory where selected MNT tiles are extracted.

    Returns
    -------
    list[Path]
        Paths to the prepared MNT files.

    Raises
    ------
    ValueError
        If required tiles cannot be found in the supplied archives.

    RuntimeError
        If the extracted MNT coverage is incomplete.
    """

    rhone_archive = Path(
        rhone_archive
    )

    ain_archive = Path(
        ain_archive
    )

    destination = Path(
        destination
    )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------------
    # Required tiles
    # ------------------------------------------------------------------------

    required_tiles = set(
        selected_tiles["ign_tile_id"]
    )

    # ------------------------------------------------------------------------
    # Inspect archives
    # ------------------------------------------------------------------------

    rhone_files = list_7z(
        rhone_archive
    )

    ain_files = list_7z(
        ain_archive
    )

    # ------------------------------------------------------------------------
    # Build archive indexes
    # ------------------------------------------------------------------------

    rhone_index = build_mnt_index(
        rhone_files
    )

    ain_index = build_mnt_index(
        ain_files
    )

    # ------------------------------------------------------------------------
    # Match required tiles
    # ------------------------------------------------------------------------

    rhone_tiles = {
        tile_id: rhone_index[tile_id]
        for tile_id in required_tiles
        if tile_id in rhone_index
    }

    ain_tiles = {
        tile_id: ain_index[tile_id]
        for tile_id in required_tiles
        if (
            tile_id not in rhone_tiles
            and tile_id in ain_index
        )
    }

    matched_tiles = (
        set(rhone_tiles)
        | set(ain_tiles)
    )

    missing_tiles = (
        required_tiles - matched_tiles
    )

    if optional_tile_ids is None:
        optional_tile_ids = set()

    required_missing_tiles = (
        missing_tiles - optional_tile_ids
    )

    optional_missing_tiles = (
        missing_tiles & optional_tile_ids
    )

    if optional_missing_tiles:
        print(
            f"Optional context tile unavailable: "
            f"{len(optional_missing_tiles):,}"
        )

    if required_missing_tiles:
        missing_preview = ", ".join(
            sorted(required_missing_tiles)[:10]
        )

        raise ValueError(
            f"{len(required_missing_tiles):,} required RGE ALTI "
            f"tile(s) were not found in the supplied archives. "
            f"First missing tiles: {missing_preview}"
        )


    # ------------------------------------------------------------------------
    # Inspect already extracted tiles
    # ------------------------------------------------------------------------

    existing_files = list(
        destination.rglob(
            "*_MNT_LAMB93_IGN69.asc"
        )
    )

    existing_index = {
        (
            f"{x:04d}_"
            f"{y:04d}"
        ): path
        for path in existing_files
        for x, y in [
            get_tile_coordinates(path)
        ]
    }

    # ------------------------------------------------------------------------
    # Determine files requiring extraction
    # ------------------------------------------------------------------------

    rhone_to_extract = [
        archive_path
        for tile_id, archive_path
        in rhone_tiles.items()
        if tile_id not in existing_index
    ]

    ain_to_extract = [
        archive_path
        for tile_id, archive_path
        in ain_tiles.items()
        if tile_id not in existing_index
    ]

    # ------------------------------------------------------------------------
    # Extract missing Rhône tiles
    # ------------------------------------------------------------------------

    if rhone_to_extract:

        extract_7z_files(
            archive=rhone_archive,
            files=rhone_to_extract,
            destination=destination,
        )

    # ------------------------------------------------------------------------
    # Extract missing Ain tiles
    # ------------------------------------------------------------------------

    if ain_to_extract:

        extract_7z_files(
            archive=ain_archive,
            files=ain_to_extract,
            destination=destination,
        )

    # ------------------------------------------------------------------------
    # Validate prepared MNT
    # ------------------------------------------------------------------------

    extracted_files = list(
        destination.rglob(
            "*_MNT_LAMB93_IGN69.asc"
        )
    )

    extracted_index = {
        (
            f"{x:04d}_"
            f"{y:04d}"
        ): path
        for path in extracted_files
        for x, y in [
            get_tile_coordinates(path)
        ]
    }

    missing_after_extraction = (
    required_tiles
    - set(extracted_index)
    )

    required_missing_after_extraction = (
        missing_after_extraction - optional_tile_ids)

    optional_missing_after_extraction = (
    missing_after_extraction & optional_tile_ids
    )

    if optional_missing_after_extraction:
        print(
            f"Optional context tiles still unavailable: "
            f"{len(optional_missing_after_extraction):,}"
        )

    if required_missing_after_extraction:

        missing_preview = ", ".join(
            sorted(
                required_missing_after_extraction
            )[:10]
        )

        raise RuntimeError(
            f"RGE ALTI extraction incomplete: "
            f"{len(required_missing_after_extraction):,} "
            f"required tile(s) are missing. "
            f"First missing tiles: {missing_preview}"
        )

    # ------------------------------------------------------------------------
    # Return available case-study and context tiles
    # ------------------------------------------------------------------------

    available_tiles = (
        required_tiles & set(extracted_index)
    )

    mnt_files = sorted(
        extracted_index[tile_id]
        for tile_id in available_tiles
    )

    print(
        f"Required MNT tiles: "
        f"{len(required_tiles):,}"
    )

    print(
        f"Rhône tiles: "
        f"{len(rhone_tiles):,}"
    )

    print(
        f"Ain tiles: "
        f"{len(ain_tiles):,}"
    )

    print(
        f"Already available: "
        f"{len(required_tiles) - len(rhone_to_extract) - len(ain_to_extract):,}"
    )

    print(
        f"Extracted: "
        f"{len(rhone_to_extract) + len(ain_to_extract):,}"
    )

    print(
        f"Prepared MNT tiles: "
        f"{len(mnt_files):,}"
    )

    return mnt_files


# ============================================================================
# Elevation processing
# ============================================================================

def compute_slope(
    elevation: np.ndarray,
    resolution_x: float,
    resolution_y: float | None = None,
) -> np.ndarray:
    """
    Compute terrain slope from an elevation raster.

    Parameters
    ----------
    elevation
        Two-dimensional elevation array.

    resolution_x
        Raster cell size along the x-axis, in metres.

    resolution_y
        Raster cell size along the y-axis, in metres.
        If omitted, square cells are assumed.

    Returns
    -------
    np.ndarray
        Terrain slope expressed as percent grade.
    """

    if resolution_y is None:
        resolution_y = resolution_x

    gradient_y, gradient_x = np.gradient(
        elevation,
        resolution_y,
        resolution_x,
    )

    return (
        np.sqrt(
            gradient_x ** 2
            + gradient_y ** 2
        )
        * 100
    )


def build_slope_raster(
    dem_path: str | Path,
    output_path: str | Path,
) -> Path:
    """
    Build a terrain slope raster from a digital elevation model.

    Slope is computed from the elevation gradient and expressed as
    percent grade. The output raster preserves the spatial reference,
    transform and extent of the input DEM.

    Parameters
    ----------
    dem_path
        Path to the input digital elevation model.

    output_path
        Path where the slope raster will be written.

    Returns
    -------
    Path
        Path to the generated slope raster.
    """

    dem_path = Path(dem_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------
    # Read DEM
    # ------------------------------------------------------------------

    with rasterio.open(dem_path) as src:

        elevation = src.read(
            1,
            masked=True,
        ).astype(
            np.float32
        )

        resolution_x = abs(src.res[0])
        resolution_y = abs(src.res[1])

        profile = src.profile.copy()

    # ------------------------------------------------------------------
    # Compute slope
    # ------------------------------------------------------------------

    elevation_array = elevation.filled(
        np.nan
    )

    slope = compute_slope(
        elevation_array,
        resolution_x=resolution_x,
        resolution_y=resolution_y,
    ).astype(
        np.float32
    )

    # Preserve invalid DEM cells.

    invalid = (
        np.ma.getmaskarray(elevation)
        | ~np.isfinite(elevation_array)
        | ~np.isfinite(slope)
    )

    nodata = -9999.0

    slope[
        invalid
    ] = nodata

    # ------------------------------------------------------------------
    # Write slope raster
    # ------------------------------------------------------------------

    profile.update(
        dtype="float32",
        count=1,
        nodata=nodata,
        compress="deflate",
    )

    with rasterio.open(
        output_path,
        "w",
        **profile,
    ) as dst:

        dst.write(
            slope,
            1,
        )

    return output_path


def resample_elevation(
    path: str | Path,
    resolution: float,
) -> np.ndarray:
    """
    Read and resample an elevation raster.

    Parameters
    ----------
    path
        Path to the elevation raster.

    resolution
        Target spatial resolution in metres.

    Returns
    -------
    np.ndarray
        Resampled elevation raster.
    """

    path = Path(path)

    with rasterio.open(path) as src:

        source_resolution = abs(
            src.res[0]
        )

        scale = (
            source_resolution
            / resolution
        )

        new_height = int(
            src.height * scale
        )

        new_width = int(
            src.width * scale
        )

        elevation = src.read(
            1,
            out_shape=(
                new_height,
                new_width,
            ),
            resampling=Resampling.average,
            masked=True,
        )

    return elevation.filled(
        np.nan
    )


# ============================================================================
# Terrain statistics
# ============================================================================

def slope_statistics(
    slope: np.ndarray,
) -> dict[str, float]:
    """
    Compute summary statistics for a slope raster.
    """

    values = slope[
        np.isfinite(slope)
    ]

    return {
        "cells": values.size,
        "mean_slope_pct": np.mean(values),
        "median_slope_pct": np.median(values),
        "p90_slope_pct": np.percentile(
            values,
            90,
        ),
        "p95_slope_pct": np.percentile(
            values,
            95,
        ),
        "p99_slope_pct": np.percentile(
            values,
            99,
        ),
        "max_slope_pct": np.max(values),
    }


def compare_municipality_slope_resolutions(
    geometry,
    mnt_files: list[Path],
    resolutions: tuple[int, ...] = (
        1,
        5,
        10,
        25,
    ),
) -> pd.DataFrame:
    """
    Compare terrain slope statistics across spatial resolutions
    for an entire municipality.

    All RGE ALTI tiles intersecting the municipality are mosaicked,
    resampled, clipped to the municipality boundary, and used to
    compute slope statistics.

    Parameters
    ----------
    geometry
        Municipality geometry in Lambert-93 coordinates.

    mnt_files
        Available RGE ALTI MNT tiles.

    resolutions
        Spatial resolutions to evaluate, in metres.

    Returns
    -------
    pandas.DataFrame
        Slope statistics for each resolution.
    """

    # ------------------------------------------------------------------------
    # Identify required RGE ALTI tiles
    # ------------------------------------------------------------------------

    tile_grid = build_tile_grid(
        geometry
    )

    required_ids = set(
        tile_grid["ign_tile_id"]
    )

    selected_files = []

    for path in mnt_files:

        tile_x, tile_y = get_tile_coordinates(
            path
        )

        tile_id = (
            f"{tile_x:04d}_"
            f"{tile_y:04d}"
        )

        if tile_id in required_ids:
            selected_files.append(
                Path(path)
            )

    if not selected_files:
        raise FileNotFoundError(
            "No RGE ALTI tiles intersect the municipality."
        )

    # ------------------------------------------------------------------------
    # Open source rasters
    # ------------------------------------------------------------------------

    sources = [
        rasterio.open(path)
        for path in selected_files
    ]

    rows = []

    try:

        for resolution in resolutions:

            # ----------------------------------------------------------------
            # Mosaic and resample
            # ----------------------------------------------------------------

            mosaic, transform = merge(
                sources,
                res=resolution,
                resampling=Resampling.average,
                nodata=np.nan,
            )

            elevation = mosaic[0].astype(
                np.float32
            )

            # ----------------------------------------------------------------
            # Municipality mask
            # ----------------------------------------------------------------

            height, width = elevation.shape

            municipality_mask = geometry_mask(
                [mapping(geometry)],
                out_shape=(
                    height,
                    width,
                ),
                transform=transform,
                invert=True,
            )

            elevation[
                ~municipality_mask
            ] = np.nan

            # ----------------------------------------------------------------
            # Terrain slope
            # ----------------------------------------------------------------

            slope = compute_slope(
                elevation,
                resolution,
            )

            statistics = slope_statistics(
                slope
            )

            statistics[
                "resolution_m"
            ] = resolution

            rows.append(
                statistics
            )

    finally:

        for source in sources:
            source.close()

    return (
        pd.DataFrame(rows)
        .set_index("resolution_m")
    )


def compare_slope_resolutions(
    path: str | Path,
    resolutions: tuple[int, ...] = (
        1,
        5,
        10,
        25,
    ),
) -> pd.DataFrame:
    """
    Compare terrain slope statistics across spatial resolutions.

    Parameters
    ----------
    path
        Path to an RGE ALTI elevation tile.

    resolutions
        Spatial resolutions to evaluate, in metres.

    Returns
    -------
    pandas.DataFrame
        Slope statistics for each resolution.
    """

    rows = []

    for resolution in resolutions:

        elevation = resample_elevation(
            path,
            resolution,
        )

        slope = compute_slope(
            elevation,
            resolution,
        )

        statistics = slope_statistics(
            slope
        )

        statistics[
            "resolution_m"
        ] = resolution

        rows.append(
            statistics
        )

    return (
        pd.DataFrame(rows)
        .set_index("resolution_m")
    )


# ============================================================================
# Municipality terrain features
# ============================================================================

def compute_municipality_terrain_features(
    municipalities: gpd.GeoDataFrame,
    dem_path: str | Path,
    slope_path: str | Path,
    municipality_column: str = "municipality",
) -> pd.DataFrame:
    """
    Compute terrain features for each municipality.

    Elevation and slope statistics are extracted from the HERMES terrain
    rasters within each municipality geometry.

    Parameters
    ----------
    municipalities
        Municipality geometries in the same projected CRS as the rasters.

    dem_path
        Path to the digital elevation model.

    slope_path
        Path to the terrain slope raster.

    municipality_column
        Column containing municipality names.

    Returns
    -------
    pandas.DataFrame
        Municipality-level terrain features.
    """

    dem_path = Path(dem_path)
    slope_path = Path(slope_path)

    rows = []

    # ------------------------------------------------------------------------
    # Open terrain rasters
    # ------------------------------------------------------------------------

    with (
        rasterio.open(dem_path) as dem_src,
        rasterio.open(slope_path) as slope_src,
    ):

        # --------------------------------------------------------------------
        # Validate spatial reference
        # --------------------------------------------------------------------

        if municipalities.crs != dem_src.crs:
            raise ValueError(
                "Municipality geometries and DEM must use the same CRS."
            )

        if slope_src.crs != dem_src.crs:
            raise ValueError(
                "DEM and slope raster must use the same CRS."
            )

        # --------------------------------------------------------------------
        # Process municipalities
        # --------------------------------------------------------------------

        for _, municipality in municipalities.iterrows():

            geometry = municipality.geometry

            # ---------------------------------------------------------------
            # Extract elevation
            # ---------------------------------------------------------------

            dem_data, _ = mask(
                dem_src,
                [mapping(geometry)],
                crop=True,
                filled=False,
            )

            elevation = dem_data[
                0
            ].compressed()

            # ---------------------------------------------------------------
            # Extract slope
            # ---------------------------------------------------------------

            slope_data, _ = mask(
                slope_src,
                [mapping(geometry)],
                crop=True,
                filled=False,
            )

            slope = slope_data[
                0
            ].compressed()

            # ---------------------------------------------------------------
            # Skip municipalities without terrain data
            # ---------------------------------------------------------------

            if (
                elevation.size == 0
                or slope.size == 0
            ):
                continue

            # ---------------------------------------------------------------
            # Compute terrain features
            # ---------------------------------------------------------------

            rows.append(
                {
                    "municipality": municipality[
                        municipality_column
                    ],
                    "elevation_mean_m": np.mean(
                        elevation
                    ),
                    "elevation_min_m": np.min(
                        elevation
                    ),
                    "elevation_max_m": np.max(
                        elevation
                    ),
                    "elevation_range_m": (
                        np.max(elevation)
                        - np.min(elevation)
                    ),
                    "slope_mean_pct": np.mean(
                        slope
                    ),
                    "slope_median_pct": np.median(
                        slope
                    ),
                    "slope_p90_pct": np.percentile(
                        slope,
                        90,
                    ),
                    "slope_p95_pct": np.percentile(
                        slope,
                        95,
                    ),
                    "share_slope_gt_5_pct": np.mean(
                        slope > 5
                    ),
                    "share_slope_gt_8_pct": np.mean(
                        slope > 8
                    ),
                    "share_slope_gt_10_pct": np.mean(
                        slope > 10
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


# ============================================================================
# Case-study DEM production
# ============================================================================

def build_case_study_dem(
    mnt_files: list[Path],
    geometry,
    output_path: str | Path,
    resolution: float = 10,
    buffer: float = 20,
    crs: str = "EPSG:2154",
) -> Path:
    """
    Build a continuous DEM for the HERMES case-study area.

    The function selects the RGE ALTI tiles intersecting the study area,
    mosaics and resamples them to the target spatial resolution, masks
    cells outside the study-area geometry, and writes the resulting DEM
    as a GeoTIFF.

    Parameters
    ----------
    mnt_files
        Available RGE ALTI MNT tiles.

    geometry
        Study-area geometry in Lambert-93 coordinates.

    output_path
        Path of the output GeoTIFF.

    resolution
        Target spatial resolution in metres.
    
    buffer
        buffer aound the study area used to select source elevation tiles, in metres.

    crs
        Coordinate reference system of the output raster.

    Returns
    -------
    Path
        Path to the generated DEM.
    """

    if isinstance(
        geometry,
        (gpd.GeoDataFrame, gpd.GeoSeries),
    ):
        geometry = geometry.geometry.union_all()

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ------------------------------------------------------------------------
    # Identify required RGE ALTI tiles
    # ------------------------------------------------------------------------

    tile_grid = build_tile_grid(
        geometry,
        crs=crs,
        buffer=buffer,
    )

    required_ids = set(
        tile_grid["ign_tile_id"]
    )

    selected_files = []

    for path in mnt_files:

        tile_x, tile_y = get_tile_coordinates(
            path
        )

        tile_id = (
            f"{tile_x:04d}_"
            f"{tile_y:04d}"
        )

        if tile_id in required_ids:
            selected_files.append(
                Path(path)
            )

    if not selected_files:
        raise FileNotFoundError(
            "No RGE ALTI tiles intersect the study area."
        )

    # ------------------------------------------------------------------------
    # Open source rasters
    # ------------------------------------------------------------------------

    sources = [
        rasterio.open(path)
        for path in selected_files
    ]

    try:

        # --------------------------------------------------------------------
        # Build continuous DEM
        # --------------------------------------------------------------------

        mosaic, transform = merge(
            sources,
            res=resolution,
            resampling=Resampling.average,
            nodata=np.nan,
            dtype="float32",
        )

        elevation = mosaic[0]

        # --------------------------------------------------------------------
        # Mask outside study area
        # --------------------------------------------------------------------

        inside = geometry_mask(
            [mapping(geometry)],
            out_shape=elevation.shape,
            transform=transform,
            invert=True,
        )

        elevation[
            ~inside
        ] = np.nan

        # --------------------------------------------------------------------
        # Write GeoTIFF
        # --------------------------------------------------------------------

        profile = {
            "driver": "GTiff",
            "height": elevation.shape[0],
            "width": elevation.shape[1],
            "count": 1,
            "dtype": "float32",
            "crs": crs,
            "transform": transform,
            "nodata": np.nan,
            "compress": "deflate",
            "tiled": True,
        }

        with rasterio.open(
            output_path,
            "w",
            **profile,
        ) as dst:

            dst.write(
                elevation.astype(
                    np.float32
                ),
                1,
            )

    finally:

        for source in sources:
            source.close()

    return output_path
