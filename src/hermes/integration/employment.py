"""
Employment integration for HERMES.

This module combines the main INSEE employment dataset with complementary Mayotte census data.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def integrate_employment(
    employment: pd.DataFrame,
    mayotte_employment: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integrate Mayotte employment data into the main employment dataset.

    Parameters
    ----------
    employment : pd.DataFrame
        Prepared INSEE employment dataset for France excluding Mayotte.

    mayotte_employment : pd.DataFrame
        Prepared Mayotte 2017 employment dataset.

    Returns
    -------
    pd.DataFrame
        Employment dataset including Mayotte.
    """

    required_columns = set(
        employment.columns
    )

    missing_columns = (
        required_columns
        - set(mayotte_employment.columns)
    )

    if missing_columns:
        raise KeyError(
            "Mayotte employment dataframe is missing columns: "
            f"{sorted(missing_columns)}"
        )

    mayotte_codes = set(
        mayotte_employment["insee_code"]
    )

    employment = employment[
        ~employment["insee_code"].isin(
            mayotte_codes
        )
    ].copy()

    mayotte = mayotte_employment[
        employment.columns
    ].copy()

    integrated = pd.concat(
        [
            employment,
            mayotte,
        ],
        ignore_index=True,
    )

    if not integrated["insee_code"].is_unique:
        raise ValueError(
            "Integrated employment dataset contains duplicate INSEE codes."
        )

    return integrated