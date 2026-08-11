"""
Municipality integration for HERMES.

This module builds the municipality reference table by
combining all prepared datasets.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd

# ============================================================================
# Public API
# ============================================================================

def build_municipality_table(
    population: pd.DataFrame,
    employment: pd.DataFrame,
    workplace_employment: pd.DataFrame,
    municipality_boundaries: pd.DataFrame,
    topography: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the municipality reference table.
    """

    municipality = (
        population
        .merge(
            employment,
            on="insee_code",
            how="left",
        )
        .merge(
            workplace_employment,
            on="insee_code",
            how="left",
        )
        .merge(
            municipality_boundaries,
            on="insee_code",
            how="left",
        )
        .merge(
            topography,
            on="insee_code",
            how="left",
        )
    )

    # ------------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------------

    if not municipality["insee_code"].is_unique:
        raise ValueError(
            "Municipality table contains duplicate INSEE codes after merging."
        )

    return municipality