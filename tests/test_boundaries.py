"""
Tests for municipality boundaries preprocessing.
"""

import geopandas as gpd
from shapely.geometry import Point

from hermes.preprocessing import prepare_municipality_boundaries


# ============================================================================
# Tests
# ============================================================================

def test_prepare_boundaries_columns():
    raw = gpd.GeoDataFrame(
        {
            "insee_com": ["01001"],
            "nom": ["Commune"],
            "insee_dep": ["01"],
            "insee_reg": ["84"],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    prepared = prepare_municipality_boundaries(raw)

    assert list(prepared.columns) == [
        "insee_code",
        "municipality",
        "department_code",
        "region_code",
        "geometry",
    ]


def test_prepare_boundaries_key_unique():
    raw = gpd.GeoDataFrame(
        {
            "insee_com": ["01001", "01002"],
            "nom": ["Commune A", "Commune B"],
            "insee_dep": ["01", "01"],
            "insee_reg": ["84", "84"],
            "geometry": [
                Point(0, 0),
                Point(1, 1),
            ],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    prepared = prepare_municipality_boundaries(raw)

    assert prepared["insee_code"].is_unique


def test_prepare_boundaries_padding():
    raw = gpd.GeoDataFrame(
        {
            "insee_com": [1001],
            "nom": ["Commune"],
            "insee_dep": [1],
            "insee_reg": [84],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    prepared = prepare_municipality_boundaries(raw)

    row = prepared.iloc[0]

    assert row["insee_code"] == "01001"
    assert row["department_code"] == "01"
    assert row["region_code"] == "84"


def test_prepare_boundaries_geometry():
    raw = gpd.GeoDataFrame(
        {
            "insee_com": ["01001"],
            "nom": ["Commune"],
            "insee_dep": ["01"],
            "insee_reg": ["84"],
            "geometry": [Point(0, 0)],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    prepared = prepare_municipality_boundaries(raw)

    assert prepared.geometry.iloc[0] == Point(0, 0)