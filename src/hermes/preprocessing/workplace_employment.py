"""
Workplace employment preprocessing for HERMES.

This module prepares the INSEE employment-at-workplace dataset.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Helpers
# ============================================================================

def _extract_indicator(
    df: pd.DataFrame,
    output_name: str,
) -> pd.DataFrame:
    """
    Convert a filtered dataframe into a standardized indicator.
    """

    indicator = (
        df[["GEO", "OBS_VALUE"]]
        .rename(
            columns={
                "GEO": "insee_code",
                "OBS_VALUE": output_name,
            }
        )
        .copy()
    )

    indicator["insee_code"] = (
        indicator["insee_code"]
        .astype(str)
        .str.zfill(5)
    )

    return indicator


# ============================================================================
# Public API
# ============================================================================

def prepare_workplace_employment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the workplace employment dataset.
    """

    filtered = df[
        (df["GEO_OBJECT"] == "COM")
        & (df["TIME_PERIOD"] == 2023)
        & (df["OBS_STATUS"] == "A")
        & (df["RP_MEASURE"] == "NBEMP")
        & (df["SEX"] == "_T")
        & (df["AGE"] == "_T")
    ].copy()

    total_jobs = _extract_indicator(
        filtered[
            (filtered["EMPFORM"] == "_T")
            & (filtered["WKTIME"] == "_T")
        ],
        "total_jobs",
    )

    salaried_jobs = _extract_indicator(
        filtered[
            (filtered["EMPFORM"] == "2")
            & (filtered["WKTIME"] == "_T")
        ],
        "salaried_jobs",
    )

    self_employed_jobs = _extract_indicator(
        filtered[
            (filtered["EMPFORM"] == "1")
            & (filtered["WKTIME"] == "_T")
        ],
        "self_employed_jobs",
    )

    full_time_jobs = _extract_indicator(
        filtered[
            (filtered["EMPFORM"] == "_T")
            & (filtered["WKTIME"] == "FT")
        ],
        "full_time_jobs",
    )

    part_time_jobs = _extract_indicator(
        filtered[
            (filtered["EMPFORM"] == "_T")
            & (filtered["WKTIME"] == "PT")
        ],
        "part_time_jobs",
    )

    prepared = (
        total_jobs
        .merge(salaried_jobs, on="insee_code")
        .merge(self_employed_jobs, on="insee_code")
        .merge(full_time_jobs, on="insee_code")
        .merge(part_time_jobs, on="insee_code")
    )

    return prepared