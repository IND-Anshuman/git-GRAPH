"""Ontology mapper class traversing behavioral and family registries."""

from typing import Optional
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry


class OntologyMapper:
    """Helper to resolve the concept context path for a canonical behavior."""

    def __init__(self, registry: CanonicalRegistry) -> None:
        self.registry = registry

    def resolve_concept_for_behavior(self, behavior_id: str) -> Optional[str]:
        """
        Traverses behavior definition to family to parent concept.
        
        Args:
            behavior_id: Unique identifier for a canonical behavior.
            
        Returns:
            Optional concept dot-path (e.g. "security.authentication").
        """
        behavior = self.registry.get_behavior(behavior_id)
        if not behavior:
            return None

        family = self.registry.get_family(behavior.family_id)
        if not family:
            return None

        return family.parent_concept_id
