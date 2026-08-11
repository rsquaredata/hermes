"""
Workplace employment integration for HERMES.

This module combines the main INSEE workplace employment dataset with complementary Mayotte census data.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def integrate_workplace_employment(
    workplace_employment: pd.DataFrame,
    mayotte_workplace_employment: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integrate Mayotte workplace employment data into the main dataset.

    Parameters
    ----------
    workplace_employment : pd.DataFrame
        Prepared INSEE workplace employment dataset for France excluding
        Mayotte.

    mayotte_workplace_employment : pd.DataFrame
        Prepared Mayotte 2017 workplace employment dataset.

    Returns
    -------
    pd.DataFrame
        Workplace employment dataset including Mayotte.
    """

    required_columns = set(
        workplace_employment.columns
    )

    missing_columns = (
        required_columns
        - set(mayotte_workplace_employment.columns)
    )

    if missing_columns:
        raise KeyError(
            "Mayotte workplace employment dataframe is missing columns: "
            f"{sorted(missing_columns)}"
        )

    mayotte_codes = set(
        mayotte_workplace_employment["insee_code"]
    )

    # ------------------------------------------------------------------------
    # Remove existing Mayotte rows
    # ------------------------------------------------------------------------

    workplace_employment = workplace_employment[
        ~workplace_employment["insee_code"].isin(
            mayotte_codes
        )
    ].copy()

    # ------------------------------------------------------------------------
    # Align schemas
    # ------------------------------------------------------------------------

    mayotte = mayotte_workplace_employment[
        workplace_employment.columns
    ].copy()

    # ------------------------------------------------------------------------
    # Combine datasets
    # ------------------------------------------------------------------------

    integrated = pd.concat(
        [
            workplace_employment,
            mayotte,
        ],
        ignore_index=True,
    )

    # ------------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------------

    if not integrated["insee_code"].is_unique:
        raise ValueError(
            "Integrated workplace employment dataset contains "
            "duplicate INSEE codes."
        )

    return integrated