"""
Data catalog for HERMES.

This module centralizes the metadata of every dataset used by the project.

The catalog acts as the single source of truth for:

- file locations
- download URLs
- documentation pages
- licenses
- formats
- spatial resolution
"""

# ============================================================================
# Standard library
# ============================================================================

from dataclasses import dataclass
from pathlib import Path

# ============================================================================
# Third-party libraries
# ============================================================================

import pandas as pd

# ============================================================================
# Local imports
# ============================================================================

from hermes.config import (
    RAW_DIR,
    PREPARED_DIR,
    GRAPH_DIR,
    MODEL_DIR,
    CACHE_DIR,
)


# ============================================================================
# Storage catalog
# ============================================================================

_STORAGE_DIRS = {
    "raw": RAW_DIR,
    "prepared": PREPARED_DIR,
    "graphs": GRAPH_DIR,
    "models": MODEL_DIR,
    "cache": CACHE_DIR,
}


# ============================================================================
# Dataset model
# ============================================================================

@dataclass
class Dataset:
    """
    Metadata describing a dataset used by HERMES.
    """

    name: str
    source: str
    download_filename: str | list[str]
    local_filename: str
    description: str

    page: str = ""
    url: str | list[str] = ""

    file_format: str = ""

    encoding: str = "utf-8"
    separator: str = ","

    spatial_resolution: str = ""
    temporal_resolution: str = ""

    license: str = ""

    dataset_id: str = ""
    vintage: int | None = None

    expected_missing: bool = False
    expected_duplicates: bool = False

    storage: str = "raw"

    @property
    def download_path(self) -> Path:
        """Return the first local download path."""
        paths = self.download_paths
        if not paths:
            raise ValueError(
                f"Dataset '{self.name}' has no download file."
            )
        return paths[0]

    @property
    def download_paths(self) -> list[Path]:
        """Return the local file paths."""
        filenames = (
            self.download_filename
            if isinstance(self.download_filename, list)
            else [self.download_filename]
        )
        return [
            RAW_DIR / filename
            for filename in filenames
            if filename
        ]

    @property
    def local_path(self) -> Path:
        """Return the dataset local path."""
        try:
            base_dir = _STORAGE_DIRS[self.storage]
        except KeyError as exc:
            raise ValueError(
                f"Unknown storage: {self.storage}"
            ) from exc

        return base_dir / self.local_filename

    @property
    def available(self) -> bool:
        """Return True if the dataset exists locally."""
        if self.local_filename:
            return self.local_path.is_file()
        paths = self.download_paths
        return bool(paths) and all(
            path.is_file()
            for path in paths
        )


# ============================================================================
# Dataset catalog
# ============================================================================

DATASETS: dict[str, Dataset] = {

    "population_raw": Dataset(
        name="Population",
        source="INSEE",
        download_filename="DS_RP_POPULATION_PRINC_2023.zip",
        local_filename="DS_RP_POPULATION_PRINC_2023_data.csv",
        description="Population census",
        page="https://www.insee.fr/fr/statistiques/9005956",
        url="https://api.insee.fr/melodi/file/DS_RP_POPULATION_PRINC/DS_RP_POPULATION_PRINC_2023_CSV_FR",
        file_format="CSV",
        encoding="latin1",
        separator=";",
        spatial_resolution="Commune",
        temporal_resolution="Annual",
        license="Open Licence 2.0",
        dataset_id="DS_RP_POPULATION_PRINC",
        vintage=2023,
        storage="raw",
    ),

    "population": Dataset(
        name="Population",
        source="HERMES",
        download_filename="",
        local_filename="population.parquet",
        description="Prepared municipality population dataset",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
    ),

    "mayotte_population_raw": Dataset(
        name="Mayotte Population",
        source="INSEE",
        download_filename="rp-mayotte-2017-ind-communes.xls",
        local_filename="rp-mayotte-2017-ind-communes.xls",
        description="2017 population census tables for the 17 municipalities of Mayotte",
        page="https://www.insee.fr/fr/statistiques/4199328?sommaire=4199393",
        url="https://www.insee.fr/fr/statistiques/fichier/4199328/rp-mayotte-2017-ind-communes.xls",
        file_format="Excel",
        spatial_resolution="Municipality",
        temporal_resolution="Census",
        license="Open Licence 2.0",
        dataset_id="rp-mayotte-2017-ind-communes",
        vintage=2017,
        storage="raw",
    ),

    "employment_raw": Dataset(
        name="Employment",
        source="INSEE",
        download_filename="DS_RP_EMPLOI_LR_PRINC_2023.zip",
        local_filename="DS_RP_EMPLOI_LR_PRINC_2023_data.csv",
        description="Labour force and unemployment",
        page="https://www.insee.fr/fr/statistiques/9002680",
        url="https://api.insee.fr/melodi/file/DS_RP_EMPLOI_LR_PRINC/DS_RP_EMPLOI_LR_PRINC_2023_CSV_FR",
        file_format="CSV",
        encoding="latin1",
        separator=";",
        spatial_resolution="Commune",
        temporal_resolution="Annual",
        license="Open Licence 2.0",
        dataset_id="DS_RP_EMPLOI_LR_PRINC",
        vintage=2023,
        expected_missing=True,
        storage="raw",
    ),

    "employment": Dataset(
        name="Employment",
        source="HERMES",
        download_filename="",
        local_filename="employment.parquet",
        description="Prepared employment dataset",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
    ),

    "mayotte_employment_raw": Dataset(
        name="Mayotte Employment",
        source="INSEE",
        download_filename="td-mayotte-pop-active-2017.zip",
        local_filename="td-mayotte-pop-active-2017.xls",
        description="2017 active population tables for the 17 municipalities of Mayotte",
        page="https://www.insee.fr/fr/statistiques/4199262?sommaire=4199393",
        url="https://www.insee.fr/fr/statistiques/fichier/4199262/td-mayotte-pop-active-2017.zip",
        file_format="Excel",
        spatial_resolution="Municipality",
        temporal_resolution="Census",
        license="Open Licence 2.0",
        dataset_id="td-mayotte-pop-active-2017",
        vintage=2017,
        storage="raw",
    ),

    "workplace_employment_raw": Dataset(
        name="Workplace Employment",
        source="INSEE",
        download_filename="DS_RP_EMPLOI_LT_PRINC_2023.zip",
        local_filename="DS_RP_EMPLOI_LT_PRINC_2023_data.csv",
        description="Employment at workplace",
        page="https://www.insee.fr/fr/statistiques/9002680",
        url="https://api.insee.fr/melodi/file/DS_RP_EMPLOI_LT_PRINC/DS_RP_EMPLOI_LT_PRINC_2023_CSV_FR",
        file_format="CSV",
        encoding="latin1",
        separator=";",
        spatial_resolution="Commune",
        temporal_resolution="Annual",
        license="Open Licence 2.0",
        dataset_id="DS_RP_EMPLOI_LT_PRINC",
        vintage=2023,
        expected_missing=True,
        storage="raw",
    ),

    "mayotte_workplace_employment_raw": Dataset(
        name="Mayotte Workplace Employment",
        source="INSEE",
        download_filename="td-mayotte-emplois-lieu-travail-2017.zip",
        local_filename="td-mayotte-emplois-lieu-travail-2017.xls",
        description="2017 workplace employment tables for the 17 municipalities of Mayotte",
        page="https://www.insee.fr/fr/statistiques/4199281?sommaire=4199393",
        url="https://www.insee.fr/fr/statistiques/fichier/4199281/td-mayotte-emplois-lieu-travail-2017.zip",
        file_format="Excel",
        spatial_resolution="Municipality",
        temporal_resolution="Census",
        license="Open Licence 2.0",
        dataset_id="td-mayotte-emplois-lieu-travail-2017",
        vintage=2017,
        storage="raw",
    ),

    "workplace_employment": Dataset(
        name="Workplace Employment",
        source="HERMES",
        download_filename="",
        local_filename="workplace_employment.parquet",
        description="Prepared workplace employment dataset",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
    ),

    "mobility_raw": Dataset(
        name="Mobility Flows",
        source="INSEE",
        download_filename="base-flux-mobilite-domicile-lieu-travail-2023_csv.zip",
        local_filename="base-flux-mobilite-domicile-lieu-travail-2023.csv",
        description="Home-to-work commuting flows between municipalities",
        page="https://www.insee.fr/fr/statistiques/8998300",
        url="https://www.insee.fr/fr/statistiques/fichier/8998300/base-flux-mobilite-domicile-lieu-travail-2023_csv.zip",
        file_format="CSV",
        encoding="utf-8",
        separator=";",
        spatial_resolution="Origin-Destination",
        temporal_resolution="Annual",
        license="Open Licence 2.0",
        dataset_id="base-flux-mobilite-domicile-lieu-travail-2023",
        vintage=2023,
        storage="raw",
    ),

    "mobility": Dataset(
        name="Mobility Flows",
        source="HERMES",
        download_filename="",
        local_filename="mobility.parquet",
        description="Prepared municipality commuting flows",
        file_format="Parquet",
        spatial_resolution="Origin-Destination",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
),

    "municipality_boundaries_raw": Dataset(
        name="Municipality Boundaries",
        source="IGN",
        download_filename="ADMIN-EXPRESS-COG_4-0__GPKG_WGS84G_FRA_2026-01-01.7z",
        local_filename="ADE-COG_4-0_GPKG_WGS84G_FRA-ED2026-01-01.gpkg",
        description="Official municipality boundaries including municipalities and arrondissements",
        page="https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_ADMIN-EXPRESS",
        url="https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG/ADMIN-EXPRESS-COG_4-0__GPKG_WGS84G_FRA_2026-01-01/ADMIN-EXPRESS-COG_4-0__GPKG_WGS84G_FRA_2026-01-01.7z",
        file_format="GPKG",
        spatial_resolution="Municipality / Municipal arrondissements",
        temporal_resolution="Annual",
        license="Open Licence 2.0",
        dataset_id="ADMIN-EXPRESS-COG_4-0",
        vintage=2026,
        storage="raw",
    ),

     "municipality_boundaries": Dataset(
        name="Municipality Boundaries",
        source="HERMES",
        download_filename="",
        local_filename="municipality_boundaries.parquet",
        description="Prepared territorial boundaries including municipalities and arrondissements",
        file_format="Parquet",
        spatial_resolution="Municipality / Municipal arrondissements",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
    ),

    "topography_raw": Dataset(
        name="Municipality Topography",
        source="Data.gouv",
        download_filename="communes-france-2026.csv",
        local_filename="communes-france-2026.csv",
        description="French municipalities geographic and topographic attributes",
        page="https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather",
        url="https://www.data.gouv.fr/api/1/datasets/r/c63fd0b1-7987-46f6-b779-8b3ed889090c",
        file_format="CSV",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="Open Licence",
        dataset_id="COMMUNES_FRANCE_2026",
        vintage=2026,
        storage="raw",
    ),

     "topography": Dataset(
        name="Municipality Topography",
        source="HERMES",
        download_filename="",
        local_filename="topography.parquet",
        description="Prepared municipality topography",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
     ),

    "climate_raw": Dataset(
        name="Climate",
        source="Météo-France",
        download_filename="6f568914-f172-455f-8c3e-ce7b29959aa7.parquet",
        local_filename="climate.parquet",
        description="Monthly SAFRAN/SIM climate dataset",
        page="https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-mensuelle",
        url="https://hydra.s3.rbx.io.cloud.ovh.net/parquet/6f568914-f172-455f-8c3e-ce7b29959aa7.parquet",
        file_format="Parquet",
        spatial_resolution="0.072° (~8 km grid)",
        temporal_resolution="Monthly",
        license="Open Licence 2.0",
        dataset_id="66159f1bf0686eb4806508e1",
        vintage=2025,
        expected_missing=True,
        storage="raw",
    ),

     "climate": Dataset(
        name="Climate",
        source="HERMES",
        download_filename="",
        local_filename="climate.parquet",
        description="Prepared municipality climate",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
     ),

    "municipality": Dataset(
        name="Municipality Table",
        source="HERMES",
        download_filename="",
        local_filename="municipality.parquet",
        description="Integrated municipality-level reference dataset",
        file_format="Parquet",
        spatial_resolution="Municipality",
        temporal_resolution="Annual",
        license="MIT",
        vintage=2026,
        storage="prepared",
),

    "electricity": Dataset(
        name="Electricity Consumption",
        source="Enedis",
        download_filename="",
        local_filename="",
        description="Electricity consumption by municipality",
        file_format="CSV",
        spatial_resolution="Commune",
        dataset_id="",
        vintage=None,
    ),

    "elevation_rhone_raw": Dataset(
        name="RGE Alti Rhône",
        source="IGN",
        download_filename="RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D069_2023-07-28.7z",
        local_filename="",
        description="RGE ALTI 1 m digital elevation model for Rhône (69)",
        page="https://www.data.gouv.fr/datasets/rge-alti-r",
        url=(
            "https://data.geopf.fr/telechargement/download/"
            "RGEALTI/"
            "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D069_2023-07-28/"
            "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D069_2023-07-28.7z"
            ),
        file_format="7z / ASCII Grid",
        spatial_resolution="1 m",
        license="Open Licence 2.0",
        dataset_id="RGEALTI_2-0.1M_D069",
        vintage=2023,
        storage="raw",
    ),

    "elevation_ain_raw": Dataset(
        name="RGE ALTI Ain",
        source="IGN",
        download_filename=[
            ("RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08.7z.001"),
            ("RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08.7z.002"),
        ],
        local_filename="",
        description=(
            "RGE ALTI 1 m digital elevation model for Ain (01), distributed as a multipart 7z archive"
        ),
        page="https://www.data.gouv.fr/datasets/rge-alti-r",
        url=[
            (
                "https://data.geopf.fr/telechargement/download/"
                "RGEALTI/"
                "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08/"
                "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08.7z.001"
            ),
            (
                "https://data.geopf.fr/telechargement/download/"
                "RGEALTI/"
                "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08/"
                "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D001_2023-08-08.7z.002"
            ),
        ],
        file_format="Multipart 7z / ASCII Grid",
        spatial_resolution="1 m",
        license="Open Licence 2.0",
        dataset_id="RGEALTI_2-0_1M_D001",
        vintage=2023,
        storage="raw",
    ),

    "elevation": Dataset(
        name="Digital Elevation Model",
        source="HERMES / IGN",
        download_filename="",
        local_filename="case_study_dem_10m.tif",
        description="10 m digital elevation model for the HERMES case-study area derived from IGN RGE ALTI 1 m",
        file_format="GeoTIFF",
        spatial_resolution="10 m",
        temporal_resolution="",
        license="Open Licence 2.0",
        dataset_id="RGEALTI_2-0",
        vintage=2023,
        storage="prepared",
    ),

    "roads": Dataset(
        name="Road Network",
        source="OpenStreetMap",
        download_filename="",
        local_filename="",
        description="Road network",
        file_format="GeoJSON",
        dataset_id="",
        vintage=None,
    ),

    "cycleways": Dataset(
        name="Cycleways",
        source="OpenStreetMap",
        download_filename="",
        local_filename="",
        description="Cycling infrastructure",
        file_format="GeoJSON",
        dataset_id="",
        vintage=None,
    ),

    "weather": Dataset(
        name="Weather",
        source="Open-Meteo",
        download_filename="",
        local_filename="",
        description="Historical weather observations",
        file_format="CSV",
        temporal_resolution="Daily",
        dataset_id="",
        vintage=None,
    ),
}


# ============================================================================
# Public API
# ============================================================================

def get_dataset(name: str) -> Dataset:
    """
    Return a dataset from its identifier.

    Raises
    ------
    KeyError
        If the dataset does not exist.
    """
    return DATASETS[name]


def list_datasets() -> list[str]:
    """Return the list of available dataset identifiers."""
    return list(DATASETS.keys())


def dataset_catalog() -> pd.DataFrame:
    """
    Return the dataset catalog as a pandas DataFrame.
    """

    rows = []

    for key, dataset in DATASETS.items():
        rows.append(
            {
                "id": key,
                "name": dataset.name,
                "source": dataset.source,
                "format": dataset.file_format,
                "resolution": dataset.spatial_resolution,
                "available": dataset.available,
                "description": dataset.description,
                "vintage": dataset.vintage,
            }
        )

    return pd.DataFrame(rows)