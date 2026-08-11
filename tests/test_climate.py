"""
Tests for climate preprocessing.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


# ============================================================================
# Local imports
# ============================================================================

from hermes.preprocessing import prepare_climate


# ============================================================================
# Tests
# ============================================================================

def test_prepare_climate_columns():
    raw = pd.DataFrame(
        {
            "LAMBX": [800000],
            "LAMBY": [6500000],
            "DATE": [202501],
            "PRENEI": [0.0],
            "PRELIQ": [52.3],
            "PRETOTM": [52.3],
            "T": [4.5],
            "EVAP": [10.2],
            "ETP": [15.6],
            "PE": [36.7],
            "SWI": [0.81],
            "DRAINC": [5.1],
            "RUNC": [2.4],
            "SPI1": [0.1],
            "SPI3": [0.2],
            "SPI6": [0.3],
            "SPI12": [0.4],
            "SSWI1": [0.5],
            "SSWI3": [0.6],
            "SSWI6": [0.7],
            "SSWI12": [0.8],
            "ECOULEMENT": [1.9],
        }
    )

    climate = prepare_climate(raw)

    assert list(climate.columns) == [
        "lambert_x",
        "lambert_y",
        "date",
        "snow_precipitation",
        "liquid_precipitation",
        "total_precipitation",
        "temperature",
        "evaporation",
        "potential_evapotranspiration",
        "water_balance",
        "soil_wetness_index",
        "drainage",
        "runoff",
        "SPI1",
        "SPI3",
        "SPI6",
        "SPI12",
        "SSWI1",
        "SSWI3",
        "SSWI6",
        "SSWI12",
        "streamflow",
        "grid_cell",
    ]


def test_prepare_climate_date():
    raw = pd.DataFrame(
        {
            "LAMBX": [800000],
            "LAMBY": [6500000],
            "DATE": [202501],
        }
    )

    climate = prepare_climate(raw)

    assert is_datetime64_any_dtype(climate["date"])
    assert climate.loc[0, "date"] == pd.Timestamp("2025-01-01")


def test_prepare_climate_grid_cell():
    raw = pd.DataFrame(
        {
            "LAMBX": [800000],
            "LAMBY": [6500000],
            "DATE": [202501],
        }
    )

    climate = prepare_climate(raw)

    assert climate.loc[0, "grid_cell"] == "800000_6500000"


def test_prepare_climate_key_unique():
    raw = pd.DataFrame(
        {
            "LAMBX": [800000, 800001],
            "LAMBY": [6500000, 6500001],
            "DATE": [202501, 202501],
        }
    )

    climate = prepare_climate(raw)

    assert (
        climate[["grid_cell", "date"]]
        .duplicated()
        .sum()
        == 0
    )

def test_prepare_climate_values():
    raw = pd.DataFrame(
        {
            "LAMBX": [800000],
            "LAMBY": [6500000],
            "DATE": [202501],
            "T": [12.3],
        }
    )

    climate = prepare_climate(raw)

    assert climate.loc[0, "temperature"] == 12.3