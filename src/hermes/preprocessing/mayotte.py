"""
Mayotte-specific preprocessing for HERMES.

This module prepares complementary INSEE 2017 census data for the 17 municipalities of Mayotte.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd


# ============================================================================
# Public API
# ============================================================================

def prepare_mayotte_population(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare Mayotte municipality population data from INSEE 2017 IND1.

    Parameters
    ----------
    df : pd.DataFrame
        Raw IND1 worksheet loaded without headers.

    Returns
    -------
    pd.DataFrame
        Prepared Mayotte population table with one row per municipality.
    """

    prepared = (
        df
        .iloc[4:21, [0, 22]]
        .copy()
    )

    prepared.columns = [
        "insee_code",
        "population",
    ]

    prepared["insee_code"] = (
        prepared["insee_code"]
        .astype(str)
        .str.zfill(5)
    )

    prepared["population"] = pd.to_numeric(
        prepared["population"],
    )

    if len(prepared) != 17:
        raise ValueError(
            "Expected 17 Mayotte municipalities, "
            f"found {len(prepared)}."
        )

    if not prepared["insee_code"].is_unique:
        raise ValueError(
            "Duplicate Mayotte municipality codes."
        )

    return prepared

def prepare_mayotte_employment(
    ind1: pd.DataFrame,
    act1: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare Mayotte employment indicators for the 17 municipalities.

    Population aged 15-64 is derived from IND1.
    Employment and unemployment are derived from ACT1.

    Parameters
    ----------
    ind1 : pd.DataFrame
        Raw IND1 worksheet loaded without headers.

    act1 : pd.DataFrame
        Raw ACT1 commune worksheet loaded without headers.

    Returns
    -------
    pd.DataFrame
        Prepared Mayotte employment table.
    """

    # ------------------------------------------------------------------------
    # Population aged 15-64 from IND1
    # ------------------------------------------------------------------------

    population_15_64 = (
        ind1
        .iloc[4:21, :22]
        .copy()
    )

    population_15_64["insee_code"] = (
        population_15_64.iloc[:, 0]
        .astype(str)
        .str.zfill(5)
    )

    # IND1 age columns:
    # 0 = code
    # 1 = municipality name
    # 2 = 0-4
    # 3 = 5-9
    # 4 = 10-14
    # 5 = 15-19
    # ...
    # 15 = 60-64
    #
    # Therefore columns 5:16 correspond to ages 15-64.

    population_15_64["population_15_64"] = (
        population_15_64
        .iloc[:, 5:16]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    population_15_64 = population_15_64[
        [
            "insee_code",
            "population_15_64",
        ]
    ]

    # ------------------------------------------------------------------------
    # Employment and unemployment from ACT1
    # ------------------------------------------------------------------------

    act1_prepared = act1.copy()

    act1_prepared.columns = (
        act1_prepared
        .iloc[10]
        .astype(str)
    )

    act1_prepared = (
        act1_prepared
        .iloc[11:28]
        .copy()
    )

    act1_prepared["CODGEO"] = (
        act1_prepared["CODGEO"]
        .astype(str)
        .str.zfill(5)
    )

    # Keep only ages 15-64.
    # Columns containing AGED65065 correspond to age 65 or more
    # and are excluded to match the national HERMES definition.

    employed_columns = [
        column
        for column in act1_prepared.columns
        if (
            "TACTR_211" in column
            and "AGED65065" not in column
        )
    ]

    unemployed_columns = [
        column
        for column in act1_prepared.columns
        if (
            "TACTR_212" in column
            and "AGED65065" not in column
        )
    ]

    act1_prepared["employed"] = (
        act1_prepared[employed_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    act1_prepared["unemployed"] = (
        act1_prepared[unemployed_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    act1_prepared["active_population"] = (
        act1_prepared["employed"]
        + act1_prepared["unemployed"]
    )

    employment = act1_prepared[
        [
            "CODGEO",
            "active_population",
            "employed",
            "unemployed",
        ]
    ].rename(
        columns={
            "CODGEO": "insee_code",
        }
    )

    # ------------------------------------------------------------------------
    # Combine employment indicators
    # ------------------------------------------------------------------------

    prepared = population_15_64.merge(
        employment,
        on="insee_code",
        how="inner",
    )

    prepared["inactive"] = (
        prepared["population_15_64"]
        - prepared["active_population"]
    )

    prepared["students"] = pd.NA
    prepared["retired"] = pd.NA
    prepared["homemakers"] = pd.NA
    prepared["other_inactive"] = pd.NA

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

    # ------------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------------

    if len(prepared) != 17:
        raise ValueError(
            "Expected 17 Mayotte municipalities, "
            f"found {len(prepared)}."
        )

    if not prepared["insee_code"].is_unique:
        raise ValueError(
            "Duplicate Mayotte municipality codes."
        )

    return prepared


def prepare_mayotte_workplace_employment(
    emp1: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare Mayotte workplace employment indicators.

    Parameters
    ----------
    emp1 : pd.DataFrame
        Raw EMP1 commune worksheet loaded without headers.

    Returns
    -------
    pd.DataFrame
        Prepared workplace employment table for Mayotte.
    """

    prepared = emp1.copy()

    prepared.columns = (
        prepared
        .iloc[10]
        .astype(str)
    )

    prepared = (
        prepared
        .iloc[11:28]
        .copy()
    )

    prepared["CODGEO"] = (
        prepared["CODGEO"]
        .astype(str)
        .str.zfill(5)
    )

    value_columns = [
        column
        for column in prepared.columns
        if column not in {
            "CODGEO",
            "LIBGEO",
        }
    ]

    salaried_columns = [
        column
        for column in value_columns
        if "_STAT10_" in column
    ]

    self_employed_columns = [
        column
        for column in value_columns
        if (
            "_STAT21_" in column
            or "_STAT22_" in column
            or "_STAT23_" in column
        )
    ]

    full_time_columns = [
        column
        for column in value_columns
        if column.endswith("_TP1")
    ]

    part_time_columns = [
        column
        for column in value_columns
        if column.endswith("_TP2")
    ]

    prepared["total_jobs"] = (
        prepared[value_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    prepared["salaried_jobs"] = (
        prepared[salaried_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    prepared["self_employed_jobs"] = (
        prepared[self_employed_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    prepared["full_time_jobs"] = (
        prepared[full_time_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    prepared["part_time_jobs"] = (
        prepared[part_time_columns]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .sum(axis=1)
    )

    prepared = prepared[
        [
            "CODGEO",
            "total_jobs",
            "salaried_jobs",
            "self_employed_jobs",
            "full_time_jobs",
            "part_time_jobs",
        ]
    ].rename(
        columns={
            "CODGEO": "insee_code",
        }
    )

    if len(prepared) != 17:
        raise ValueError(
            "Expected 17 Mayotte municipalities, "
            f"found {len(prepared)}."
        )

    if not prepared["insee_code"].is_unique:
        raise ValueError(
            "Duplicate Mayotte municipality codes."
        )

    return prepared