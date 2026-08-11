"""
Population preprocessing for HERMES.

This module transforms the raw INSEE population dataset into a municipality-level dataset ready for simulation.

Preparation steps

1. Keep municipalities (COM) and municipal arrondissements (ARM)
2. Keep year 2023
3. Keep total population (_T)
4. Keep validated observations (A)
5. Rename columns
6. Format INSEE codes

"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def prepare_population(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the INSEE population dataset for HERMES.

    The function keeps only:
    - municipalities (COM)
    - year 2023
    - total population
    - validated observations

    Parameters
    ----------
    df : pd.DataFrame
        Raw INSEE population dataset.

    Returns
    -------
    pd.DataFrame
        Municipality-level population table.
    """

    population = df[
        (df["GEO_OBJECT"].isin(
            [
                "COM",
                "ARM"
            ]
        ))
        & (df["TIME_PERIOD"] == 2023)
        & (df["SEX"] == "_T")
        & (df["AGE"] == "_T")
        & (df["OBS_STATUS"] == "A")
    ].copy()

    prepared = (
        population.rename(
            columns={
                "GEO": "insee_code",
                "OBS_VALUE": "population",
            }
        )[["insee_code", "population"]]
    )

    prepared["insee_code"] = (
            prepared["insee_code"]
            .astype(str)
            .str.zfill(5)
    )
    return prepared