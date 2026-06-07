"""Enum defining directed relationship types between concepts."""

from enum import Enum


class ConceptRelationshipType(str, Enum):
    """Types of semantic and structural links between different concepts."""

    DEPENDS_ON = "DEPENDS_ON"
    """Concept A relies on Concept B's capabilities."""

    IMPLEMENTS = "IMPLEMENTS"
    """Concept A implements abstract interface/contract defined by Concept B."""

    SUPPORTS = "SUPPORTS"
    """Concept A supports or directly assists the execution of Concept B."""

    USES = "USES"
    """Concept A utilizes specific elements of Concept B's functionalities."""

    REQUIRES = "REQUIRES"
    """Concept A strictly requires Concept B to function."""

    ENHANCES = "ENHANCES"
    """Concept A extends or optimizes the functionality of Concept B."""

    REPLACES = "REPLACES"
    """Concept A has taken over or replaced the capabilities of Concept B."""
