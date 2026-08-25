"""
IGN data sources for HERMES.
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path
import shutil

# ============================================================================
# Local imports
# ============================================================================

from hermes.data_catalog import get_dataset
from hermes.io import download_file


# ============================================================================
# Public API
# ============================================================================

def download_municipality_boundaries(
    overwrite: bool = False,
) -> Path:
    """
    Download IGN Admin Express COG municipality boundaries.

    The downloaded 7z archive is extracted automatically. The GeoPackage
    is then located recursively and moved to the canonical HERMES raw-data
    location.

    Parameters
    ----------
    overwrite : bool, default=False
        Whether to overwrite existing files.

    Returns
    -------
    Path
        Path to the municipality boundaries GeoPackage.
    """

    dataset = get_dataset(
        "municipality_boundaries_raw"
    )

    # ------------------------------------------------------------------------
    # Existing dataset
    # ------------------------------------------------------------------------

    if dataset.local_path.exists() and not overwrite:
        return dataset.local_path

    # ------------------------------------------------------------------------
    # Download and extract archive
    # ------------------------------------------------------------------------

    archive_path = download_file(
        url=dataset.url,
        destination=dataset.download_path,
        overwrite=overwrite,
    )

    # ------------------------------------------------------------------------
    # Locate extracted GeoPackage
    # ------------------------------------------------------------------------

    matches = list(
        archive_path.parent.rglob(
            dataset.local_filename
        )
    )

    if not matches:
        raise FileNotFoundError(
            "IGN GeoPackage not found after archive extraction: "
            f"{dataset.local_filename}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "Multiple IGN GeoPackages found after archive extraction: "
            f"{matches}"
        )

    extracted_path = matches[0]

    # ------------------------------------------------------------------------
    # Move to canonical raw-data location
    # ------------------------------------------------------------------------

    if extracted_path != dataset.local_path:

        dataset.local_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if dataset.local_path.exists():
            dataset.local_path.unlink()

        shutil.move(
            extracted_path,
            dataset.local_path,
        )

    return dataset.local_path