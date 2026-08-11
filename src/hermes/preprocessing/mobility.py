"""
Mobility preprocessing for HERMES.

This module prepares municipality-to-municipality commuting flows.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Private helpers
# ============================================================================

def _normalize_insee_code(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize municipality identifiers.

    Numeric municipality codes may be read as floating-point values
    by pandas. Trailing decimal parts are removed and numeric INSEE
    codes are padded to five characters. Non-numeric identifiers,
    such as foreign destination codes, are preserved.
    """

    normalized = (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True,
        )
    )

    numeric_mask = normalized.str.fullmatch(
        r"\d+",
        na=False,
    )

    normalized.loc[numeric_mask] = (
        normalized.loc[numeric_mask]
        .str.zfill(5)
    )

    return normalized


# ============================================================================
# Public API
# ============================================================================

def prepare_mobility(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare municipality-to-municipality commuting flows.
    """

    prepared = (
        df.rename(
            columns={
                "CODGEO": "origin_insee_code",
                "LIBGEO": "origin_name",
                "DCLT": "destination_insee_code",
                "L_DCLT": "destination_name",
                "NBFLUX_C23_ACTOCC15P": "commuters",
            }
        )
        .copy()
    )

    prepared["origin_insee_code"] = (
        _normalize_insee_code(
            prepared["origin_insee_code"]
        )
    )

    prepared["destination_insee_code"] = (
        _normalize_insee_code(
            prepared["destination_insee_code"]
        )
    )

    return prepared