"""
Topography preprocessing for HERMES.

This module prepares municipality topography indicators.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def prepare_topography(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the municipality topography dataset.
    """

    prepared = (
        df[
            [
                "code_insee",
                "superficie_hectare",
                "altitude_moyenne",
                "altitude_minimale",
                "altitude_maximale",
                "latitude_centre",
                "longitude_centre",
            ]
        ]
        .rename(
            columns={
                "code_insee": "insee_code",
                "superficie_hectare": "area_hectares",
                "altitude_moyenne": "mean_elevation",
                "altitude_minimale": "min_elevation",
                "altitude_maximale": "max_elevation",
                "latitude_centre": "latitude",
                "longitude_centre": "longitude",
            }
        )
        .copy()
    )

    prepared["insee_code"] = (
        prepared["insee_code"]
        .astype(str)
        .str.zfill(5)
    )

    return prepared