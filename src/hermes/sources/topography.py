"""
Topography dataset download utilities.
"""

# ============================================================================
# Local imports
# ============================================================================

from hermes.data_catalog import get_dataset
from hermes.io import download_file


# ============================================================================
# Public API
# ============================================================================

def download_topography() -> None:
    """
    Download the municipality topography dataset.
    """

    dataset = get_dataset("topography")

    download_file(
        url=dataset.url,
        destination=dataset.local_path,
    )