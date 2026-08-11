"""
Logging configuration for HERMES.
"""

# ============================================================================
# Imports
# ============================================================================

import logging


# ============================================================================
# Configure HERMES logger
# ============================================================================

handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(levelname)s | %(name)s | %(message)s"
)

handler.setFormatter(formatter)

logger = logging.getLogger("hermes")

if not logger.handlers:
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False