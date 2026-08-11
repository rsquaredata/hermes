"""
Configuration module for HERMES.

This module centralizes all project paths and global constants.
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path


# ============================================================================
# Project paths
# ============================================================================

# Project root
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Main directories
DATA_DIR = PROJECT_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PREPARED_DIR = DATA_DIR / "prepared"
EXTERNAL_DIR = DATA_DIR / "external"

GRAPH_DIR = DATA_DIR / "graphs"
MODEL_DIR = DATA_DIR / "models"
CACHE_DIR = DATA_DIR / "cache"

NOTEBOOKS_DIR = PROJECT_DIR / "notebooks"
DOCS_DIR = PROJECT_DIR / "docs"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
ASSETS_DIR = PROJECT_DIR / "assets"
FIGURES_DIR = ASSETS_DIR / "figures"

RGE_ALTI_MNT_DIR = (
    RAW_DIR
    / "rge_alti"
    / "case_study_mnt"
)


# ============================================================================
# Create directories
# ============================================================================

for directory in (
    DATA_DIR,
    RAW_DIR,
    PREPARED_DIR,
    EXTERNAL_DIR,
    GRAPH_DIR,
    MODEL_DIR,
    CACHE_DIR,
    NOTEBOOKS_DIR,
    DOCS_DIR,
    OUTPUTS_DIR,
):
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================================
# General settings
# ============================================================================

CITY = "Villefranche-sur-Saône"
COUNTRY = "France"

RANDOM_STATE = 42


# ============================================================================
# Coordinate Reference Systems
# ============================================================================

CRS_WGS84 = "EPSG:4326"
CRS_LAMBERT93 = "EPSG:2154"