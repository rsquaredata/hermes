"""
Generic I/O utilities for HERMES.
"""

# ============================================================================
# Imports
# ============================================================================

from pathlib import Path
import logging
import zipfile

import pandas as pd
import py7zr
import requests
from tqdm import tqdm


# ============================================================================
# Logger
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Public API
# ============================================================================

def download_file(
    url: str,
    destination: Path,
    overwrite: bool = False,
    timeout: int = 60,
) -> Path:
    """
    Download a file.

    If the downloaded file is a ZIP or 7z archive, it is automatically extracted.

    Parameters
    ----------
    url : str
        File URL.
    destination : Path
        Output path.
    overwrite : bool, default=False
        Whether to overwrite an existing file.
    timeout : int, default=60
        HTTP request timeout in seconds.

    Returns
    -------
    Path
        Downloaded file.
    """

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if destination.exists() and not overwrite:
        logger.info(
            "File already exists: %s",
            destination.resolve(),
        )
        return destination

    logger.info(
        "Downloading: %s",
        destination.name,
    )

    response = requests.get(
        url,
        stream=True,
        timeout=timeout,
    )
    response.raise_for_status()

    total_size = int(
        response.headers.get("content-length", 0)
    )

    with (
        open(destination, "wb") as file,
        tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=destination.name,
        ) as progress,
    ):
        for chunk in response.iter_content(
            chunk_size=8192,
        ):
            if chunk:
                file.write(chunk)
                progress.update(len(chunk))

    # ------------------------------------------------------------------------
    # Extract archive
    # ------------------------------------------------------------------------

    if zipfile.is_zipfile(destination):

        with zipfile.ZipFile(destination) as archive:
            archive.extractall(destination.parent)

        logger.info(
            "Zip archive extracted: %s",
            destination.name,
        )

    elif destination.suffix.lower() == ".7z":

        with  py7zr.SevenZipFile(
            destination,
            mode="r",
        ) as archive:
            archive.extractall(
                path=destination.parent,
             )

        logger.info(
            "7z archive extracted: %s",
            destination.name,
        )

    logger.info(
        "Download completed: %s",
        destination.name,
    )

    return destination


def save_dataframe(
    df: pd.DataFrame,
    path: str | Path,
    overwrite: bool = True,
) -> Path:
    """
    Save a DataFrame as a Parquet file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    path : str | Path
        Output file path.
    overwrite : bool, default=True
        Whether to overwrite an existing file.

    Returns
    -------
    Path
        Path to the saved file.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if path.exists():

        if not overwrite:
            raise FileExistsError(
                f"{path} already exists."
            )

        logger.warning(
            "Overwriting existing file: %s",
            path.resolve(),
        )

    else:

        logger.info(
            "Creating file: %s",
            path.resolve(),
        )

    df.to_parquet(
        path,
        index=False,
    )

    logger.info(
        "Dataset saved: %s",
        path.resolve(),
    )

    return path


def load_dataframe(
    path: str | Path,
) -> pd.DataFrame:
    """
    Load a Parquet DataFrame.

    Parameters
    ----------
    path : str | Path
        Input file.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.
    """

    logger.info(
        "Loading dataset: %s",
        Path(path).resolve(),
    )

    return pd.read_parquet(path)