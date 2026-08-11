"""
Territorial graph statistics for HERMES.

This module computes descriptive statistics for the HERMES
territorial graph.
"""

# ============================================================================
# Third-party libraries
# ============================================================================

import logging

import networkx as nx
import pandas as pd


# ============================================================================
# Logger
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Public API
# ============================================================================

def graph_statistics(
    graph: nx.DiGraph,
) -> None:
    """
    Display descriptive statistics for the territorial graph.
    """

    logger.info("=" * 80)
    logger.info("Graph statistics")
    logger.info("=" * 80)

    logger.info("Nodes: %s", f"{graph.number_of_nodes():,}")
    logger.info("Edges: %s", f"{graph.number_of_edges():,}")
    logger.info(
        "Density: %.6f",
        nx.density(graph),
    )
    logger.info(
        "Self-loops: %s",
        f"{nx.number_of_selfloops(graph):,}",
    )
    logger.info(
        "Weakly connected components: %s",
        nx.number_weakly_connected_components(graph),
    )
    logger.info(
        "Strongly connected components: %s",
        nx.number_strongly_connected_components(graph),
    )

    logger.info("")

    describe_graph(graph)


# ============================================================================
# Degree statistics
# ============================================================================

def describe_graph(
    graph: nx.DiGraph,
) -> None:
    """
    Display degree statistics.
    """

    stats = pd.DataFrame(
        {
            "in_degree": dict(
                graph.in_degree()
            ),
            "out_degree": dict(
                graph.out_degree()
            ),
            "degree": dict(
                graph.degree()
            ),
        }
    )

    logger.info("Degree summary")

    print(
        stats.describe()
    )