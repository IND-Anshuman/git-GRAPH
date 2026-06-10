from dataclasses import dataclass

@dataclass(frozen=True)
class SemanticRelationshipType:
    """Ontology-backed semantic type for relationships, replacing static Enums."""
    id: str
    category: str
    name: str
    parent_type: str | None = None
