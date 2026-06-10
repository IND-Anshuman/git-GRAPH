from dataclasses import dataclass

@dataclass(frozen=True)
class SemanticType:
    """Ontology-backed semantic type for entities, replacing static Enums."""
    id: str
    category: str
    name: str
    parent_type: str | None = None
