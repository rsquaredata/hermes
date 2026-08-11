"""
Utility functions for HERMES.

This module contains reusable helpers shared across the project.

Current utilities include:

- dataset downloads
- streamed file downloads with progress reporting
- ZIP archive extraction
- 7z archive extraction
- automatic dataset preparation
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path
import shutil
import subprocess
import zipfile

# ============================================================================
# Third-party libraries
# ============================================================================

import requests
from tqdm import tqdm

# ============================================================================
# Local imports
# ============================================================================

from hermes.data_catalog import get_dataset


# ============================================================================
# Constants
# ============================================================================

DEFAULT_CHUNK_SIZE = 1024 * 1024
DEFAULT_TIMEOUT = 60


# ============================================================================
# Download utilities
# ============================================================================

def download_file(
    url: str,
    destination: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
) -> Path:
    """
    Download a file if it is not already available locally.

    Parameters
    ----------
    url
        Remote file URL.

    destination
        Local destination path.

    chunk_size
        Download chunk size in bytes.

    timeout
        HTTP request timeout in seconds.

    Returns
    -------
    Path
        Local path of the downloaded file.
    """

    if destination.exists():
        print(
            f"Already downloaded: {destination.name}"
        )
        return destination

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Downloading: {destination.name}"
    )

    with requests.get(
        url,
        stream=True,
        timeout=timeout,
    ) as response:

        response.raise_for_status()

        total_size = int(
            response.headers.get(
                "content-length",
                0,
            )
        )

        with destination.open("wb") as file:

            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress:

                for chunk in response.iter_content(
                    chunk_size=chunk_size,
                ):

                    if not chunk:
                        continue

                    file.write(chunk)
                    progress.update(
                        len(chunk)
                    )

    return destination


def download_dataset(
    name: str,
) -> list[Path]:
    """
    Download all files associated with a catalog dataset.

    Parameters
    ----------
    name
        Dataset identifier from the HERMES data catalog.

    Returns
    -------
    list[Path]
        Paths of downloaded files.
    """

    dataset = get_dataset(name)

    urls = (
        dataset.url
        if isinstance(dataset.url, list)
        else [dataset.url]
    )

    paths = dataset.download_paths

    if len(urls) != len(paths):
        raise ValueError(
            f"URL/file mismatch for dataset '{name}': "
            f"{len(urls)} URL(s) for {len(paths)} file(s)."
        )

    downloaded_paths = []

    for url, path in zip(
        urls,
        paths,
        strict=True,
    ):

        downloaded_paths.append(
            download_file(
                url=url,
                destination=path,
            )
        )

    return downloaded_paths


# ============================================================================
# Archive utilities
# ============================================================================

def extract_zip(
    archive: Path,
    destination: Path,
) -> Path:
    """
    Extract a ZIP archive.

    Parameters
    ----------
    archive
        Path to the ZIP archive.

    destination
        Directory where the archive must be extracted.

    Returns
    -------
    Path
        Extraction directory.
    """

    if not archive.exists():
        raise FileNotFoundError(
            f"Archive not found: {archive}"
        )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Extracting: {archive.name}"
    )

    with zipfile.ZipFile(
        archive,
        "r",
    ) as zip_file:

        zip_file.extractall(
            destination
        )

    return destination


def extract_7z(
    archive: Path,
    destination: Path,
) -> Path:
    """
    Extract a 7z archive.

    Multipart archives must be passed using their first `.001` file.
    7-Zip automatically locates subsequent archive parts stored in the
    same directory.

    Parameters
    ----------
    archive
        Path to the 7z archive or first multipart archive file.

    destination
        Directory where the archive must be extracted.

    Returns
    -------
    Path
        Extraction directory.
    """

    if not archive.exists():
        raise FileNotFoundError(
            f"Archive not found: {archive}"
        )

    if shutil.which("7z") is None:
        raise RuntimeError(
            "7z executable not found. "
            "Install p7zip before extracting 7z archives."
        )

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Extracting: {archive.name}"
    )

    subprocess.run(
        [
            "7z",
            "x",
            str(archive),
            f"-o{destination}",
            "-y",
        ],
        check=True,
    )

    return destination

def extract_7z_files(
    archive: Path,
    files: list[str],
    destination: Path,
) -> Path:
    """
    Extract selected files from a 7z archive without preserving
    the archive directory structure.

    Multipart archives must be passed using their first `.001` file.

    Parameters
    ----------
    archive
        Path to the 7z archive or first multipart archive file.

    files
        Paths of files to extract from the archive.

    destination
        Directory where selected files must be extracted.

    Returns
    -------
    Path
        Extraction directory.
    """

    if not archive.exists():
        raise FileNotFoundError(
            f"Archive not found: {archive}"
        )

    if shutil.which("7z") is None:
        raise RuntimeError(
            "7z executable not found. "
            "Install p7zip before extracting 7z archives."
        )

    if not files:
        print(
            f"No files to extract from: {archive.name}"
        )
        return destination

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Extracting {len(files):,} file(s) "
        f"from: {archive.name}"
    )

    subprocess.run(
        [
            "7z",
            "e",
            str(archive),
            *files,
            f"-o{destination}",
            "-y",
        ],
        check=True,
    )

    return destination

def list_7z(
    archive: Path,
) -> list[str]:
    """
    List files contained in a 7z archive without extracting them.

    Multipart archives must be passed using their first `.001` file.

    Parameters
    ----------
    archive
        Path to the 7z archive or first multipart archive file.

    Returns
    -------
    list[str]
        Paths of files contained in the archive.
    """

    if not archive.exists():
        raise FileNotFoundError(
            f"Archive not found: {archive}"
        )

    if shutil.which("7z") is None:
        raise RuntimeError(
            "7z executable not found. "
            "Install p7zip before reading 7z archives."
        )

    result = subprocess.run(
        [
            "7z",
            "l",
            "-slt",
            str(archive),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    files = []

    for line in result.stdout.splitlines():

        if line.startswith("Path = "):

            path = line.removeprefix(
                "Path = "
            )

            if path != str(archive):
                files.append(path)

    return files


# ============================================================================
# Dataset preparation
# ============================================================================

def prepare_dataset(
    name: str,
    extract_dir: Path | None = None,
) -> list[Path]:
    """
    Download a dataset and extract archives when necessary.

    Supported inputs include:

    - direct files such as CSV, XLS, XLSX and Parquet
    - ZIP archives
    - 7z archives
    - multipart 7z archives beginning with `.7z.001`

    Parameters
    ----------
    name
        Dataset identifier from the HERMES data catalog.

    extract_dir
        Optional extraction directory. If omitted, archives are
        extracted next to the downloaded archive.

    Returns
    -------
    list[Path]
        Downloaded files for direct datasets, or extraction
        directories for archived datasets.
    """

    paths = download_dataset(name)

    if not paths:
        return []

    first_path = paths[0]

    destination = (
        extract_dir
        if extract_dir is not None
        else first_path.parent
    )

    filename = first_path.name.lower()

    # ------------------------------------------------------------------------
    # ZIP archive
    # ------------------------------------------------------------------------

    if filename.endswith(".zip"):

        extract_zip(
            first_path,
            destination,
        )

        return [destination]

    # ------------------------------------------------------------------------
    # Standard 7z archive
    # ------------------------------------------------------------------------

    if filename.endswith(".7z"):

        extract_7z(
            first_path,
            destination,
        )

        return [destination]

    # ------------------------------------------------------------------------
    # Multipart 7z archive
    # ------------------------------------------------------------------------

    if filename.endswith(".7z.001"):

        extract_7z(
            first_path,
            destination,
        )

        return [destination]

    # ------------------------------------------------------------------------
    # Direct file
    # ------------------------------------------------------------------------

    return paths