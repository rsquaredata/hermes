"""
Employment preprocessing for HERMES.

This module transforms the raw INSEE employment dataset into a municipality-level dataset ready for simulation.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Constants
# ============================================================================

EMPLOYMENT_STATUS = {
    "_T": "population_15_64",
    "1": "employed",
    "2": "unemployed",
    "1T2": "active_population",
    "3": "inactive",
    "31": "students",
    "33": "retired",
    "35": "homemakers",
    "36": "other_inactive",
}


# ============================================================================
# Public API
# ============================================================================

def prepare_employment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the INSEE employment dataset for HERMES.

    The function:

    - keeps municipalities ("COM") and arrondissements ("ARM");
    - keeps year 2023;
    - keeps both sexes;
    - keeps the total education level;
    - keeps validated observations;
    - pivots employment status into columns.

    Parameters
    ----------
    df : pd.DataFrame
        Raw INSEE employment dataset.

    Returns
    -------
    pd.DataFrame
        Municipality-level employment table.
    """

    filtered = df[
        (df["GEO_OBJECT"].isin(
            [
                "COM",
                "ARM"
            ]
        ))
        & (df["TIME_PERIOD"] == 2023)
        & (df["SEX"] == "_T")
        & (df["AGE"] == "Y15T64")
        & (df["EDUC"] == "_T")
        & (df["OBS_STATUS"] == "A")
        & (df["EMPSTA_ENQ"].isin(EMPLOYMENT_STATUS))
    ].copy()

    prepared = (
        filtered
        .pivot(
            index="GEO",
            columns="EMPSTA_ENQ",
            values="OBS_VALUE",
        )
        .rename(columns=EMPLOYMENT_STATUS)
        .reset_index()
        .rename(columns={"GEO": "insee_code"})
    )

    prepared["insee_code"] = (
        prepared["insee_code"]
        .astype(str)
        .str.zfill(5)
    )

    prepared = prepared[
        [
            "insee_code",
            "population_15_64",
            "active_population",
            "employed",
            "unemployed",
            "inactive",
            "students",
            "retired",
            "homemakers",
            "other_inactive",
        ]
    ]

    prepared.columns.name = None
    
    return prepared