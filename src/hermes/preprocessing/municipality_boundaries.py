"""
Municipality boundaries preprocessing for HERMES.

This module prepares the territorial reference from IGN Admin Express COG
municipality and municipal arrondissement layers.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import geopandas as gpd
import pandas as pd


# ============================================================================
# Constants
# ============================================================================

BOUNDARY_COLUMNS = [
    "insee_code",
    "municipality",
    "entity_type",
    "parent_insee_code",
    "department_code",
    "region_code",
    "geometry",
]


# ============================================================================
# Private helpers
# ============================================================================

def _prepare_communes(
    communes: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Prepare the IGN municipality layer.
    """

    prepared = (
        communes.rename(
            columns={
                "code_insee": "insee_code",
                "nom_officiel": "municipality",
                "code_insee_du_departement": "department_code",
                "code_insee_de_la_region": "region_code",
                "superficie_cadastrale": "area_hectares",
            }
        )
        .copy()
    )

    prepared["entity_type"] = "COMMUNE"
    prepared["parent_insee_code"] = pd.NA

    return prepared[BOUNDARY_COLUMNS]


def _prepare_arrondissements(
    arrondissements: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Prepare the IGN municipal arrondissement layer.
    """

    prepared = (
        arrondissements.rename(
            columns={
                "code_insee": "insee_code",
                "nom_officiel": "municipality",
                "code_insee_de_la_commune_de_rattach": "parent_insee_code",
            }
        )
        .copy()
    )

    prepared["entity_type"] = "ARRONDISSEMENT_MUNICIPAL"

    # Department and region codes are derived from the parent municipality
    # later, after communes and arrondissements have been combined.
    prepared["department_code"] = pd.NA
    prepared["region_code"] = pd.NA

    return prepared[BOUNDARY_COLUMNS]


# ============================================================================
# Public API
# ============================================================================

def prepare_municipality_boundaries(
    communes: gpd.GeoDataFrame,
    arrondissements: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Prepare the HERMES municipality boundary reference.

    The resulting dataset contains both municipalities and municipal
    arrondissements for Paris, Lyon, and Marseille.

    Parameters
    ----------
    communes : gpd.GeoDataFrame
        IGN municipality layer.

    arrondissements : gpd.GeoDataFrame
        IGN municipal arrondissement layer.

    Returns
    -------
    gpd.GeoDataFrame
        Territorial boundary reference containing municipalities and
        municipal arrondissements.
    """

    prepared_communes = _prepare_communes(
        communes,
    )

    prepared_arrondissements = _prepare_arrondissements(
        arrondissements,
    )

    # ------------------------------------------------------------------------
    # Add parent municipality attributes to municipal arrondissements
    # ------------------------------------------------------------------------

    parent_reference = prepared_communes[
        [
            "insee_code",
            "department_code",
            "region_code",
        ]
    ].rename(
        columns={
            "insee_code": "parent_insee_code",
            "department_code": "parent_department_code",
            "region_code": "parent_region_code",
        }
    )

    prepared_arrondissements = prepared_arrondissements.merge(
        parent_reference,
        on="parent_insee_code",
        how="left",
    )

    prepared_arrondissements["department_code"] = (
        prepared_arrondissements["parent_department_code"]
    )

    prepared_arrondissements["region_code"] = (
        prepared_arrondissements["parent_region_code"]
    )

    prepared_arrondissements = prepared_arrondissements.drop(
        columns=[
            "parent_department_code",
            "parent_region_code",
        ]
    )

    # ------------------------------------------------------------------------
    # Combine territorial units
    # ------------------------------------------------------------------------

    prepared = pd.concat(
        [
            prepared_communes,
            prepared_arrondissements,
        ],
        ignore_index=True,
    )

    prepared = gpd.GeoDataFrame(
        prepared,
        geometry="geometry",
        crs=communes.crs,
    )

    # ------------------------------------------------------------------------
    # Standardize identifiers
    # ------------------------------------------------------------------------

    prepared["insee_code"] = (
        prepared["insee_code"]
        .astype("string")
        .str.zfill(5)
    )

    prepared["parent_insee_code"] = (
        prepared["parent_insee_code"]
        .astype("string")
        .str.zfill(5)
    )

    prepared["department_code"] = (
        prepared["department_code"]
        .astype("string")
        .str.zfill(2)
    )

    prepared["region_code"] = (
        prepared["region_code"]
        .astype("string")
        .str.zfill(2)
    )

    # ------------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------------

    if not prepared["insee_code"].is_unique:
        duplicates = (
            prepared.loc[
                prepared["insee_code"].duplicated(
                    keep=False,
                ),
                "insee_code",
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            "Duplicate territorial INSEE codes after preprocessing: "
            f"{duplicates}"
        )

    missing_parent = prepared.loc[
        (
            prepared["entity_type"]
            == "ARRONDISSEMENT_MUNICIPAL"
        )
        & prepared["parent_insee_code"].isna()
    ]

    if not missing_parent.empty:
        raise ValueError(
            "Municipal arrondissements without parent municipality: "
            f"{missing_parent['insee_code'].tolist()}"
        )

    return prepared