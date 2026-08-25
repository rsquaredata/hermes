"""
Climate dataset.
"""

from hermes.data_catalog import get_dataset
from hermes.io import download_file


def download_climate(
    overwrite: bool = False,
):
    dataset = get_dataset("climate")

    return download_file(
        url=dataset.url,
        destination=dataset.local_path,
        overwrite=overwrite,
    )