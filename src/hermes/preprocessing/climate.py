"""
Climate preprocessing for HERMES.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def prepare_climate(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the monthly SAFRAN/SIM climate dataset.
    """

    climate = (
        df.rename(
            columns={
                "LAMBX": "lambert_x",
                "LAMBY": "lambert_y",
                "DATE": "date",
                "PRENEI": "snow_precipitation",
                "PRELIQ": "liquid_precipitation",
                "PRETOTM": "total_precipitation",
                "T": "temperature",
                "EVAP": "evaporation",
                "ETP": "potential_evapotranspiration",
                "PE": "water_balance",
                "SWI": "soil_wetness_index",
                "DRAINC": "drainage",
                "RUNC": "runoff",
                "ECOULEMENT": "streamflow",
            }
        )
        .copy()
    )

    climate["date"] = pd.to_datetime(
        climate["date"],
        format="%Y%m",
    )

    climate["grid_cell"] = (
        climate["lambert_x"].astype(int).astype(str)
        + "_"
        + climate["lambert_y"].astype(int).astype(str)
    )

    return climate