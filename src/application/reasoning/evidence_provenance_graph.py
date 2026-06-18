"""
Phase 7A — EvidenceProvenanceGraph

Tracks the full audit trail of *how* a reasoning conclusion was reached by
recording the directed acyclic graph (DAG) of evidence nodes and derivation
edges that led to it.

Purpose
-------
Every reasoning conclusion in Phase 7 must have a provenance DAG so that:

  * **Auditability**    — external reviewers can trace why a result was produced.
  * **Reproducibility** — the same DAG inputs reproduce the same conclusion.
  * **Governance**      — compliance checks can verify which sources were used.
  * **Explanation**     — UI explanation generators walk the DAG top-down.

DAG Structure
-------------
::

    [Capability node]
          │
       derived_from
          ▼
     [Flow node]
          │
       derived_from
          ▼
     [Entity node]
          │
       derived_from
          ▼
   [Relationship node]
          │
       derived_from
          ▼
    [Conclusion node]

Example provenance payload
--------------------------
::

    {
        "conclusion": "Authentication is critical",
        "derived_from": [
            "capability_auth",
            "flow_login",
            "entity_auth_service",
            "dependency_postgres"
        ]
    }
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProvenanceNode:
    """A single node in the provenance DAG.

    Attributes:
        node_id:    Unique identifier (e.g. ``"capability_auth"``).
        node_type:  Category of this node (``"capability"``, ``"flow"``, …).
        label:      Human-readable display label.
        metadata:   Arbitrary extra data (file, line, commit, etc.).
    """

    node_id: str
    node_type: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "metadata": self.metadata,
        }


@dataclass
class ProvenanceEdge:
    """A directed edge in the provenance DAG.

    Attributes:
        from_id:       Source node_id.
        to_id:         Target node_id.
        relationship:  Edge label (e.g. ``"derived_from"``, ``"supports"``).
    """

    from_id: str
    to_id: str
    relationship: str = "derived_from"

    def to_dict(self) -> dict[str, str]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "relationship": self.relationship,
        }


@dataclass
class EvidenceProvenanceGraph:
    """Full provenance DAG for a single reasoning conclusion.

    Attributes:
        conclusion_id:  Unique identifier for this conclusion / result.
        conclusion:     Human-readable conclusion statement.
        nodes:          All nodes in the DAG (evidence sources + conclusion).
        edges:          Directed edges expressing derivation relationships.
    """

    conclusion_id: str
    conclusion: str
    nodes: list[ProvenanceNode] = field(default_factory=list)
    edges: list[ProvenanceEdge] = field(default_factory=list)

    # ── Mutation helpers ──────────────────────────────────────────────────────

    def add_node(self, node: ProvenanceNode) -> None:
        """Add a node to the DAG (deduplicates by node_id)."""
        existing_ids = {n.node_id for n in self.nodes}
        if node.node_id not in existing_ids:
            self.nodes.append(node)

    def add_edge(self, edge: ProvenanceEdge) -> None:
        """Add a directed edge to the DAG."""
        self.edges.append(edge)

    def derived_from(self) -> list[str]:
        """Return the flat list of source node_ids that feed this conclusion."""
        conclusion_ids = {n.node_id for n in self.nodes if n.node_type == "conclusion"}
        return [
            e.from_id
            for e in self.edges
            if e.to_id in conclusion_ids and e.relationship == "derived_from"
        ]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "conclusion_id": self.conclusion_id,
            "conclusion": self.conclusion,
            "derived_from": self.derived_from(),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def empty(cls, conclusion_id: str, conclusion: str) -> "EvidenceProvenanceGraph":
        """Create an empty provenance graph for the given conclusion."""
        return cls(conclusion_id=conclusion_id, conclusion=conclusion)
