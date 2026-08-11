"""
Coverage comparison utilities for HERMES.

This module compares municipality coverage across datasets.
"""

# ============================================================================
# Imports
# ============================================================================

import logging

import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================================
# Public API
# ============================================================================

def compare_dataset_coverage(
    **datasets: pd.DataFrame,
) -> None:
    """
    Compare municipality coverage across datasets.

    Parameters
    ----------
    **datasets
        Named DataFrames containing an ``insee_code`` column.
    """

    logger.info("=" * 80)
    logger.info("Dataset coverage")
    logger.info("=" * 80)

    # ------------------------------------------------------------------------
    # Dataset sizes
    # ------------------------------------------------------------------------

    for name, df in datasets.items():

        logger.info(
            "%-25s %7s municipalities",
            name,
            f"{len(df):,}",
        )

    # ------------------------------------------------------------------------
    # Reference dataset
    # ------------------------------------------------------------------------

    reference_name = next(iter(datasets))
    reference_codes = set(
        datasets[reference_name]["insee_code"]
    )

    logger.info("")
    logger.info(
        "Reference dataset: %s",
        reference_name,
    )

    # ------------------------------------------------------------------------
    # Coverage differences
    # ------------------------------------------------------------------------

    for name, df in list(datasets.items())[1:]:

        codes = set(df["insee_code"])

        only_in_dataset = sorted(
            codes - reference_codes
        )

        missing_from_dataset = sorted(
            reference_codes - codes
        )

        if only_in_dataset:

            logger.warning(
                "%s: %s municipalities not present in %s",
                name,
                len(only_in_dataset),
                reference_name,
            )

        if missing_from_dataset:

            logger.warning(
                "%s: missing %s municipalities from %s",
                name,
                len(missing_from_dataset),
                reference_name,
            )

        if (
            not only_in_dataset
            and not missing_from_dataset
        ):

            logger.info(
                "%s: identical coverage",
                name,
            )