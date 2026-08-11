"""
Validation utilities for HERMES.

This module provides reusable functions for exploring
and validating datasets.
"""

# ============================================================================
# Imports
# ============================================================================

# Standard library
from dataclasses import dataclass
import logging

# Third-party libraries
import pandas as pd
from IPython.display import display


# ============================================================================
# Validation model
# ============================================================================

@dataclass(slots=True)
class ValidationResult:
    """
    Result of a validation check.
    """

    name: str
    value: str
    level: str = "info"
    message: str | None = None


# ============================================================================
# Logger
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Data exploration
# ============================================================================

def explore_dataframe(
    df: pd.DataFrame,
    title: str = "DataFrame Overview",
    preview_rows: int = 5,
) -> None:
    """
    Display an overview of a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to explore.
    title : str, default="DataFrame Overview"
        Section title.
    preview_rows : int, default=5
        Number of rows displayed in the preview.
    """

    logger.info("=" * 80)
    logger.info(title)
    logger.info("=" * 80)

    rows, cols = df.shape

    memory = (
        df.memory_usage(deep=True)
        .sum()
        / 1024**2
    )

    logger.info("Rows: %s", f"{rows:,}")
    logger.info("Columns: %s", cols)
    logger.info("Memory: %.2f MB", memory)

    logger.info("Column summary")

    display(
        pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Non-null count": df.count().values,
                "Missing": df.isna().sum().values,
            }
        )
    )

    numeric = df.select_dtypes(
        include="number",
    )

    if not numeric.empty:

        logger.info("Numeric summary")

        display(
            numeric.describe()
        )

    categorical = df.select_dtypes(
        include=[
            "object",
            "category",
        ],
    )

    if not categorical.empty:

        logger.info("Categorical summary")

        display(
            categorical.describe()
        )

    logger.info(
        "First %s rows",
        preview_rows,
    )

    display(
        df.head(preview_rows)
    )


# ============================================================================
# Data validation
# ============================================================================

def validate_dataframe(
    df: pd.DataFrame,
    key: str | list[str] | None = None,
    expect_missing: bool = False,
    expect_duplicates: bool = False,
    expected_missing_columns: list[str] | None = None,
) -> None:
    """
    Validate a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    key : str | list[str], optional
        Primary key column or composite primary key.
    expect_missing : bool, default=False
        Whether missing values are allowed.
    expect_duplicates : bool, default=False
        Whether duplicate rows are allowed.
    expected_missing_columns: list[str], optional
        Columns for which missing values are expected.
    """

    logger.info("=" * 80)
    logger.info("Dataset validation")
    logger.info("=" * 80)

    issues: list[str] = []

    # ------------------------------------------------------------------------
    # Duplicate rows
    # ------------------------------------------------------------------------

    duplicates = df.duplicated().sum()

    if duplicates == 0:

        logger.info("Duplicate rows: 0")

    elif expect_duplicates:

        logger.warning(
            "Duplicate rows: %s (expected)",
            duplicates,
        )

    else:

        logger.warning(
            "Duplicate rows: %s",
            duplicates,
        )

        issues.append("duplicate rows")

    # ------------------------------------------------------------------------
    # Missing values
    # ------------------------------------------------------------------------

    missing_per_column = (
        df.isna()
        .sum()
        .loc[lambda s: s > 0]
    )

    if missing_per_column.empty:

        logger.info("Missing values: 0")

    else:

        logger.warning(
            "Missing values: %s",
            int(missing_per_column.sum()),
        )

        if expected_missing_columns is not None:

            unexpected = [
                column
                for column in missing_per_column.index
                if column not in expected_missing_columns
            ]

            for column, count in missing_per_column.items():

                if column in expected_missing_columns:

                    logger.info(
                        "✓ %s: %s missing values (expected)",
                        column,
                        int(count),
                    )

                else:

                    logger.error(
                        "✗ %s: %s missing values (unexpected)",
                        column,
                        int(count),
                    )

            if unexpected:
                issues.append("unexpected missing values")

        elif expect_missing:

            logger.info(
                "Missing values are expected."
            )

        else:

            issues.append("missing values")

    # ------------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------------

    if key is not None:

        # Normalize to a list
        keys = [key] if isinstance(key, str) else key

        # Check that all key columns exist
        missing_columns = [
            column
            for column in keys
            if column not in df.columns
        ]

        if missing_columns:

            logger.error(
                "Primary key column(s) not found: %s",
                ", ".join(missing_columns),
            )

            issues.append("primary key not found")

        else:

         logger.info(
                "Primary key: (%s)",
                ", ".join(keys),
            )

        unique = not df.duplicated(
            subset=keys,
        ).any()

        missing_key = (
            df[keys]
            .isna()
            .any(axis=1)
            .sum()
        )

        if unique:

            logger.info(
                "Primary key is unique."
            )

        else:

            logger.warning(
                "Primary key is not unique."
            )

            issues.append("primary key not unique")

        if missing_key == 0:

            logger.info(
                    "Primary key contains no missing values.",
                )

        else:

            logger.warning(
                "Missing keys: %s",
                missing_key,
            )

            issues.append("missing primary keys")

    # ------------------------------------------------------------------------
    # Final status
    # ------------------------------------------------------------------------

    if not issues:

        logger.info("Validation passed.")

    else:

        logger.error(
            "Validation failed: %s",
            ", ".join(issues),
        )