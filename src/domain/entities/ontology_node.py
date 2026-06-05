"""Domain entity representing a single node in the behavioral ontology tree."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class OntologyNode:
    """
    An OntologyNode is one vertex in the hierarchical ontology that classifies
    code behaviors (e.g., Security → Authentication → Hash_Comparison).

    The ontology is loaded from YAML at startup.  Leaf nodes are the terminal
    classification targets that LogicSignatures reference via ontology_node_id.
    """

    id: str
    """Dot-path identifier that is globally unique (e.g., 'security.authentication.hash_comparison')."""

    name: str
    """Display name for this node (e.g., 'Hash Comparison')."""

    parent_id: str | None
    """Dot-path of the parent node.  None for root-level domain nodes."""

    domain: str
    """Top-level domain this node belongs to (e.g., 'Security', 'Data_Management')."""

    description: str
    """Human-readable description of what behaviors this node encompasses."""

    ontology_version: str
    """Version string of the ontology YAML that defined this node (e.g., '2.1.0')."""

    is_leaf: bool = False
    """True if this node has no children and can be assigned to a LogicSignature."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary extensible metadata."""

    loaded_at: datetime = field(default_factory=datetime.utcnow)
    """UTC timestamp when this node was loaded into the database."""

    def full_path(self) -> str:
        """
        Return a formatted path representation of this node's dot-path ID.

        Each segment is title-cased and the separator changes from '.' to '/'.

        Example:
            'security.authentication.hash_comparison'
            → 'Security/Authentication/Hash_Comparison'

        Returns:
            A slash-separated, title-cased path string.
        """
        return "/".join(segment.title() for segment in self.id.split("."))

    def is_root(self) -> bool:
        """
        Return True if this node has no parent (i.e., it is a top-level domain node).

        Returns:
            True when parent_id is None.
        """
        return self.parent_id is None
