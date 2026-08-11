"""
Territorial graph export for HERMES.

This module exports and imports HERMES territorial graphs.
"""

# ============================================================================
# Standard library
# ============================================================================

from pathlib import Path

# ============================================================================
# Third-party libraries
# ============================================================================

import networkx as nx
import numpy as np
import pandas as pd


# ============================================================================
# Private helpers
# ============================================================================

def _clean_graphml_attributes(
    attributes: dict,
) -> None:
    """
    Clean attributes before GraphML serialization.

    GraphML only supports basic scalar types. Geometry, missing values, and 
    NumPy scalar types therefore require special handling.
    """

    for key in list(attributes):

        value = attributes[key]

        # --------------------------------------------------------------------
        # Remove geometry
        # --------------------------------------------------------------------

        # Geometry is stored separately in the prepared municipality dataset
        # and may be encoded as binary WKB, which GraphML cannot serialize.
        if key == "geometry":
            del attributes[key]
            continue

        # --------------------------------------------------------------------
        # Remove missing values
        # --------------------------------------------------------------------

        # GraphML cannot serialize pandas.NA or NumPy NaN values.
        if pd.isna(value):
            del attributes[key]
            continue

        # --------------------------------------------------------------------
        # Convert NumPy scalar types
        # --------------------------------------------------------------------

        # GraphML expects native Python scalar types.
        if isinstance(value, np.generic):
            attributes[key] = value.item()


# ============================================================================
# Public API
# ============================================================================

def export_graphml(
    graph: nx.DiGraph,
    output_path: str | Path,
) -> Path:
    """
    Export a graph to GraphML.

    Unsupported attributes such as geometry and missing values are excluded from 
    the exported representation. NumPy scalar values are converted to native 
    Python types.

    Parameters
    ----------
    graph
        Territorial graph.
    output_path
        Output GraphML file.

    Returns
    -------
    Path
        Path to the exported GraphML file.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    export_graph = graph.copy()

    # ------------------------------------------------------------------------
    # Clean node attributes
    # ------------------------------------------------------------------------

    for _, attributes in export_graph.nodes(
        data=True,
    ):
        _clean_graphml_attributes(
            attributes,
        )

    # ------------------------------------------------------------------------
    # Clean edge attributes
    # ------------------------------------------------------------------------

    for _, _, attributes in export_graph.edges(
        data=True,
    ):
        _clean_graphml_attributes(
            attributes,
        )

    # ------------------------------------------------------------------------
    # Export graph
    # ------------------------------------------------------------------------

    nx.write_graphml(
        export_graph,
        output_path,
    )

    return output_path


def load_graphml(
    input_path: str | Path,
) -> nx.DiGraph:
    """
    Load a GraphML graph.

    Parameters
    ----------
    input_path
        GraphML file.

    Returns
    -------
    nx.DiGraph
        Territorial graph.
    """

    return nx.read_graphml(
        Path(input_path),
    )