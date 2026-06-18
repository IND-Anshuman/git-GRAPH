"""
Phase 7A — ReasoningSnapshot

Ties a reasoning run to a *specific, immutable point-in-time state* of the
knowledge graph so that the same question can be re-executed later and any
difference in result can be attributed to a graph state change rather than
reasoning drift.

Without a snapshot:

    "Why is Authentication critical?" answered today
    "Why is Authentication critical?" answered 3 months later
    → *Different answers with no traceability of why they differ.*

With a snapshot the diff between two reasoning runs is fully explainable
by diffing the graph state at the two snapshot timestamps.

Fields
------
repository_id:     UUID of the repository the reasoning was performed over.
commit_hash:       Git commit SHA at the time of the reasoning run.
capability_version: Version hash of the compiled capability graph.
ontology_version:   Version hash of the ontology / concept graph.
compiler_version:   Semantic compiler engine version string.
reasoning_version:  Phase 7 engine version string (semver format).
snapshot_at:        UTC timestamp when the snapshot was recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ReasoningSnapshot:
    """Immutable record of the graph state at reasoning execution time."""

    repository_id: str
    commit_hash: str
    capability_version: str
    ontology_version: str
    compiler_version: str
    reasoning_version: str
    snapshot_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return {
            "repository_id": self.repository_id,
            "commit_hash": self.commit_hash,
            "capability_version": self.capability_version,
            "ontology_version": self.ontology_version,
            "compiler_version": self.compiler_version,
            "reasoning_version": self.reasoning_version,
            "snapshot_at": self.snapshot_at.isoformat(),
        }

    @classmethod
    def unknown(cls, repository_id: str, commit_hash: str) -> "ReasoningSnapshot":
        """Factory for a snapshot where version metadata is not yet available."""
        return cls(
            repository_id=repository_id,
            commit_hash=commit_hash,
            capability_version="unknown",
            ontology_version="unknown",
            compiler_version="unknown",
            reasoning_version="7A.0",
        )
