"""
Tests for topography preprocessing.
"""

import pandas as pd

from hermes.preprocessing import prepare_topography


def test_prepare_topography_columns():
    raw = pd.DataFrame(
        {
            "code_insee": ["01001"],
            "superficie_hectare": [500],
            "altitude_moyenne": [250],
            "altitude_minimale": [200],
            "altitude_maximale": [300],
            "latitude_centre": [46.1],
            "longitude_centre": [5.1],
        }
    )

    prepared = prepare_topography(raw)

    assert list(prepared.columns) == [
        "insee_code",
        "area_hectares",
        "mean_elevation",
        "min_elevation",
        "max_elevation",
        "latitude",
        "longitude",
    ]


def test_prepare_topography_key_unique():
    raw = pd.DataFrame(
        {
            "code_insee": ["01001", "01002"],
            "superficie_hectare": [100, 200],
            "altitude_moyenne": [10, 20],
            "altitude_minimale": [5, 15],
            "altitude_maximale": [15, 25],
            "latitude_centre": [45.0, 46.0],
            "longitude_centre": [5.0, 6.0],
        }
    )

    prepared = prepare_topography(raw)

    assert prepared["insee_code"].is_unique