"""
Population integration for HERMES.

This module combines the main INSEE population dataset with complementary Mayotte census data.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def integrate_population(
    population: pd.DataFrame,
    mayotte_population: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integrate Mayotte population data into the main population dataset.

    The main INSEE 2023 population dataset covers France excluding Mayotte.
    Mayotte municipalities are completed using the 2017 census.

    Parameters
    ----------
    population : pd.DataFrame
        Prepared INSEE population dataset for France excluding Mayotte.

    mayotte_population : pd.DataFrame
        Prepared Mayotte 2017 municipality population dataset.

    Returns
    -------
    pd.DataFrame
        Population dataset including Mayotte.
    """

    # ------------------------------------------------------------------------
    # Validate columns
    # ------------------------------------------------------------------------

    required_columns = {
        "insee_code",
        "population",
    }

    missing_population_columns = (
        required_columns - set(population.columns)
    )

    if missing_population_columns:
        raise KeyError(
            "Population dataframe is missing columns: "
            f"{sorted(missing_population_columns)}"
        )

    missing_mayotte_columns = (
        required_columns - set(mayotte_population.columns)
    )

    if missing_mayotte_columns:
        raise KeyError(
            "Mayotte population dataframe is missing columns: "
            f"{sorted(missing_mayotte_columns)}"
        )

    # ------------------------------------------------------------------------
    # Remove existing Mayotte municipalities
    # ------------------------------------------------------------------------

    mayotte_codes = set(
        mayotte_population["insee_code"]
    )

    population = population[
        ~population["insee_code"].isin(
            mayotte_codes
        )
    ].copy()

    # ------------------------------------------------------------------------
    # Align schemas
    # ------------------------------------------------------------------------

    mayotte = mayotte_population.copy()

    for column in population.columns:
        if column not in mayotte.columns:
            mayotte[column] = pd.NA

    mayotte = mayotte[population.columns]

    # ------------------------------------------------------------------------
    # Combine datasets
    # ------------------------------------------------------------------------

    integrated = pd.concat(
        [
            population,
            mayotte,
        ],
        ignore_index=True,
    )

    # ------------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------------

    if not integrated["insee_code"].is_unique:
        raise ValueError(
            "Integrated population dataset contains duplicate INSEE codes."
        )

    return integrated