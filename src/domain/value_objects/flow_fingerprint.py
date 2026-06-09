"""Value object representing the structural signature of a flow sequence."""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class FlowFingerprint:
    """Contains signature metrics of a traced flow to compare flows structurally."""

    node_sequence: List[str] = field(default_factory=list)
    hop_count: int = 0
    boundary_count: int = 0
    calls_signature: str = ""

    def calculate_similarity(self, other: "FlowFingerprint") -> float:
        """Computes the similarity score in [0.0, 1.0] between two flow signatures.

        Formula:
        Similarity = 0.40 * NodeSequence + 0.30 * CallsSignature + 0.15 * HopCount + 0.15 * BoundaryCount
        """
        # 1. Node Sequence Jaccard
        seq1 = set(self.node_sequence)
        seq2 = set(other.node_sequence)
        if not seq1 and not seq2:
            seq_sim = 1.0
        elif not seq1 or not seq2:
            seq_sim = 0.0
        else:
            seq_sim = len(seq1.intersection(seq2)) / len(seq1.union(seq2))

        # 2. Calls Signature Jaccard
        tokens1 = set(t for t in re.split(r"[,\s]+", self.calls_signature) if t)
        tokens2 = set(t for t in re.split(r"[,\s]+", other.calls_signature) if t)
        if not tokens1 and not tokens2:
            calls_sim = 1.0
        elif not tokens1 or not tokens2:
            calls_sim = 0.0
        else:
            calls_sim = len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))

        # 3. Hop count similarity
        max_hops = max(self.hop_count, other.hop_count, 1)
        hop_sim = 1.0 - (abs(self.hop_count - other.hop_count) / max_hops)

        # 4. Boundary count similarity
        max_bounds = max(self.boundary_count, other.boundary_count, 1)
        boundary_sim = 1.0 - (abs(self.boundary_count - other.boundary_count) / max_bounds)

        return (
            0.40 * seq_sim
            + 0.30 * calls_sim
            + 0.15 * hop_sim
            + 0.15 * boundary_sim
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this value object to a dictionary."""
        return {
            "node_sequence": self.node_sequence,
            "hop_count": self.hop_count,
            "boundary_count": self.boundary_count,
            "calls_signature": self.calls_signature,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FlowFingerprint":
        """Deserializes a dictionary to a FlowFingerprint."""
        if not d:
            return cls()
        return cls(
            node_sequence=list(d.get("node_sequence", [])),
            hop_count=int(d.get("hop_count", 0)),
            boundary_count=int(d.get("boundary_count", 0)),
            calls_signature=str(d.get("calls_signature", "")),
        )
