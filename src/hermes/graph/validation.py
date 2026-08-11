"""
Territorial graph validation for HERMES.

This module validates the integrity of the HERMES territorial graph.
"""

# ============================================================================
# Standard library
# ============================================================================

from dataclasses import dataclass
import logging

# ============================================================================
# Third-party libraries
# ============================================================================

import networkx as nx


# ============================================================================
# Logger
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# Validation model
# ============================================================================

@dataclass(slots=True)
class ValidationResult:
    """
    Result of a validation check.
    """

    name: str
    value: str
    level: str = "info"
    message: str | None = None


# ============================================================================
# Public API
# ============================================================================

def validate_graph(
    graph: nx.DiGraph,
) -> None:
    """
    Validate the territorial graph.

    Raises
    ------
    ValueError
        If one or more validation checks fail.
    """

    logger.info("=" * 80)
    logger.info("Graph validation")
    logger.info("=" * 80)

    results = [
        _validate_nodes(graph),
        _validate_edges(graph),
        _validate_self_loops(graph),
        _validate_isolated_nodes(graph),
        _validate_connectivity(graph),
    ]

    for result in results:
        logger.info(
            "%-35s %s",
            result.name + ":",
            result.value,
        )

    logger.info("=" * 80)

    errors = [
        result.message
        for result in results
        if result.level == "error"
        and result.message is not None
    ]

    if errors:

        logger.error("Graph validation failed.")

        for error in errors:
            logger.error("- %s", error)

        raise ValueError(
            "\n".join(errors)
        )

    logger.info("✓ Graph validation successful.")


# ============================================================================
# Validation functions
# ============================================================================

def _validate_nodes(
    graph: nx.DiGraph,
) -> ValidationResult:
    """
    Validate graph nodes.
    """

    n = graph.number_of_nodes()

    if n == 0:
        return ValidationResult(
            name="Nodes",
            value="0",
            level="error",
            message="Graph contains no nodes.",
        )

    return ValidationResult(
        name="Nodes",
        value=f"{n:,}",
    )


def _validate_edges(
    graph: nx.DiGraph,
) -> ValidationResult:
    """
    Validate graph edges.
    """

    n = graph.number_of_edges()

    if n == 0:
        return ValidationResult(
            name="Edges",
            value="0",
            level="error",
            message="Graph contains no edges.",
        )

    return ValidationResult(
        name="Edges",
        value=f"{n:,}",
    )


def _validate_self_loops(
    graph: nx.DiGraph,
) -> ValidationResult:
    """
    Report self-loops.

    Self-loops represent intra-municipality commuting flows and are valid in the HERMES territorial graph.
    """

    loops = nx.number_of_selfloops(
        graph
    )

    return ValidationResult(
        name="Self-loops",
        value=f"{loops:,}",
        level="info",
    )


def _validate_isolated_nodes(
    graph: nx.DiGraph,
) -> ValidationResult:
    """
    Report isolated municipalities.
    """

    isolated = len(
        list(
            nx.isolates(graph)
        )
    )

    level = (
        "warning"
        if isolated
        else "info"
    )

    message = (
        "Some municipalities have no incoming "
        "or outgoing commuting flows."
        if isolated
        else None
    )

    return ValidationResult(
        name="Isolated municipalities",
        value=f"{isolated:,}",
        level=level,
        message=message,
    )


def _validate_connectivity(
    graph: nx.DiGraph,
) -> ValidationResult:
    """
    Report graph connectivity.
    """

    weak = nx.number_weakly_connected_components(
        graph
    )

    return ValidationResult(
        name="Weakly connected components",
        value=f"{weak:,}",
        level=(
            "warning"
            if weak > 1
            else "info"
        ),
        message=(
            "Graph contains multiple weakly "
            "connected components."
            if weak > 1
            else None
        ),
    )