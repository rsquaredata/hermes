"""
Dataset loading utilities for HERMES.

This module provides helper functions for loading datasets
defined in the data catalog.
"""

# ============================================================================
# Standard library
# ============================================================================

# No standard library imports

# ============================================================================
# Third-party libraries
# ============================================================================

import geopandas as gpd
import pandas as pd

# ============================================================================
# Local imports
# ============================================================================

from hermes.data_catalog import Dataset, get_dataset


# ============================================================================
# Supported loaders
# ============================================================================

LOADERS = {
    ".csv": pd.read_csv,
    ".geojson": gpd.read_file,
    ".gpkg": gpd.read_file,
    ".shp": gpd.read_file,
    ".parquet": pd.read_parquet,
}


# ============================================================================
# Generic loader
# ============================================================================

def load_dataset(dataset_name: str, **kwargs):
    """
    Load a dataset from the data catalog.
    """

    dataset = get_dataset(dataset_name)

    if not dataset.available:
        raise FileNotFoundError(
            f"{dataset.local_filename} not found.\n"
            "Please download the dataset first."
        )

    suffix = dataset.local_path.suffix.lower()

    loader = LOADERS.get(suffix)

    if loader is None:
        raise ValueError(
            f"Unsupported file format: {suffix}"
        )

    if suffix == ".csv":
        kwargs.setdefault("encoding", dataset.encoding)
        kwargs.setdefault("sep", dataset.separator)

    return loader(dataset.local_path, **kwargs)

# ============================================================================
# Dataset-specific loaders
# ============================================================================


def load_population_raw(**kwargs):
    return load_dataset("population_raw", **kwargs)

def load_population(**kwargs):
    """Load the population dataset."""
    return load_dataset("population", **kwargs)


def load_employment_raw(**kwargs):
    return load_dataset("employment_raw", **kwargs)

def load_employment(**kwargs):
    """Load the employment dataset."""
    return load_dataset("employment", **kwargs)

def load_workplace_employment_raw(**kwargs):
    return load_dataset("workplace_employment_raw", **kwargs)

def load_workplace_employment(**kwargs):
    """Load the workplace employment dataset."""
    return load_dataset("workplace_employment", **kwargs)

def load_mobility_raw(**kwargs):
    return load_dataset("mobility_raw", **kwargs)

def load_mobility(**kwargs):
    """Load the mobility dataset."""
    return load_dataset("mobility", **kwargs)

def load_municipality_boundaries_raw():
    """Load the raw municipality boundaries dataset."""
    dataset = get_dataset("municipality_boundaries_raw")
    return gpd.read_file(dataset.local_path, layer="commune")

def load_municipality_boundaries(**kwargs):
    """Load the prepared municipality boundaries dataset."""
    return load_dataset("municipality_boundaries",**kwargs)

def load_topography_raw():
    return load_dataset("topography_raw")

def load_topography():
    """Load the municipality topography dataset."""
    return load_dataset("topography")

def load_climate_raw(**kwargs):
    return load_dataset("climate_raw", **kwargs)

def load_climate(**kwargs):
    """Load the climate dataset."""
    return load_dataset("climate", **kwargs)

def load_municipality(**kwargs):
    """Load the integrated municipality table."""
    return load_dataset("municipality", **kwargs)

def load_electricity(**kwargs):
    """Load the electricity dataset."""
    return load_dataset("electricity", **kwargs)


def load_elevation(**kwargs):
    """Load the elevation dataset."""
    return load_dataset("elevation", **kwargs)


def load_roads(**kwargs):
    """Load the road network dataset."""
    return load_dataset("roads", **kwargs)


def load_cycleways(**kwargs):
    """Load the cycling infrastructure dataset."""
    return load_dataset("cycleways", **kwargs)


def load_weather(**kwargs):
    """Load the weather dataset."""
    return load_dataset("weather", **kwargs)