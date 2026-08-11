"""
Territorial graph construction for HERMES.

This module builds the territorial graph from the municipality
reference table and commuting flows.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import networkx as nx
import pandas as pd
import logging

# ============================================================================
# Local imports
# ============================================================================

from hermes.graph.constants import (
    EDGE_SOURCE,
    EDGE_TARGET,
    EDGE_WEIGHT,
    NODE_ID,
)

# ============================================================================
# Logger
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# Public API
# ============================================================================

def build_graph(
    municipality: pd.DataFrame,
    mobility: pd.DataFrame,
) -> nx.DiGraph:
    """
    Build the HERMES territorial graph.

    Parameters
    ----------
    municipality
        Municipality reference table.

    mobility
        Municipality commuting flows.

    Returns
    -------
    nx.DiGraph
        Directed territorial graph.
    """

    # ------------------------------------------------------------------------
    # Validate municipality dataframe
    # ------------------------------------------------------------------------

    required_node_columns = {
        NODE_ID,
    }

    missing_node_columns = (
        required_node_columns
        - set(municipality.columns)
    )

    if missing_node_columns:
        raise KeyError(
            "Municipality dataframe is missing columns: "
            f"{sorted(missing_node_columns)}"
        )

    # ------------------------------------------------------------------------
    # Validate mobility dataframe
    # ------------------------------------------------------------------------

    required_edge_columns = {
        EDGE_SOURCE,
        EDGE_TARGET,
        EDGE_WEIGHT,
    }

    missing_edge_columns = (
        required_edge_columns
        - set(mobility.columns)
    )

    if missing_edge_columns:
        raise KeyError(
            "Mobility dataframe is missing columns: "
            f"{sorted(missing_edge_columns)}"
        )

    # ------------------------------------------------------------------------
    # Remove edges with missing municipalities
    # ------------------------------------------------------------------------

    invalid_edges = mobility[
        mobility[
            [
                EDGE_SOURCE,
                EDGE_TARGET,
            ]
        ].isna().any(axis=1)
    ]

    if not invalid_edges.empty:
        print(
            f"Ignoring {len(invalid_edges)} mobility flows "
            "with missing municipality codes."
        )

    mobility = mobility.dropna(
        subset=[
            EDGE_SOURCE,
            EDGE_TARGET,
        ]
    ).copy()


    # ------------------------------------------------------------------------
    # Create graph
    # ------------------------------------------------------------------------

    graph = nx.DiGraph()

    # ------------------------------------------------------------------------
    # Add municipality nodes
    # ------------------------------------------------------------------------

    node_columns = [
        column
        for column in municipality.columns
        if column != NODE_ID
    ]

    for values in municipality.itertuples(
        index=False,
        name=None,
    ):

        node = str(values[0])

        attributes = dict(
            zip(
                node_columns,
                values[1:],
                strict=True,
            )
        )

        graph.add_node(
            node,
            **attributes,
        )

    # ------------------------------------------------------------------------
    # Add mobility edges
    # ------------------------------------------------------------------------

    edge_columns = list(mobility.columns)

    source_idx = edge_columns.index(EDGE_SOURCE)
    target_idx = edge_columns.index(EDGE_TARGET)
    weight_idx = edge_columns.index(EDGE_WEIGHT)

    ignored_edges = 0

    for values in mobility.itertuples(
        index=False,
        name=None,
    ):

        origin = str(values[source_idx])
        destination = str(values[target_idx])

        if (
            origin not in graph
            or destination not in graph
        ):
            ignored_edges += 1
            continue

        graph.add_edge(
            origin,
            destination,
            **{
                EDGE_WEIGHT: values[weight_idx],
            },
        )

    if ignored_edges:
        logger.warning(
            "Ignored %d mobility flows whose origin or destination "
            "is outside the HERMES territorial graph.",
            ignored_edges,
        )
    
    return graph