"""Enum defining concept evolution transition types."""

from enum import Enum


class ConceptTransitionType(str, Enum):
    """Transition types representing the chronological evolution steps of a concept."""

    CONCEPT_CREATION = "CONCEPT_CREATION"
    """First appearance of the concept in the commit history."""

    CONCEPT_MODIFICATION = "CONCEPT_MODIFICATION"
    """Refactoring or updating code implementing the concept without changing its core definition."""

    CONCEPT_SPLIT = "CONCEPT_SPLIT"
    """A concept splitting into multiple sub-concepts."""

    CONCEPT_MERGE = "CONCEPT_MERGE"
    """Multiple concepts merging into a single consolidated concept."""

    CONCEPT_REMOVAL = "CONCEPT_REMOVAL"
    """Complete removal of the concept's implementing code (transitions to INACTIVE)."""
