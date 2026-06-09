"""Value object representing evidence that supports a concept or capability candidate."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class CandidateEvidence:
    """Grounding tokens supporting a dynamic concept or capability candidate."""

    supporting_entities: List[str] = field(default_factory=list)
    supporting_relationships: List[str] = field(default_factory=list)
    supporting_behaviors: List[str] = field(default_factory=list)
    supporting_flows: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this value object to a dictionary."""
        return {
            "supporting_entities": self.supporting_entities,
            "supporting_relationships": self.supporting_relationships,
            "supporting_behaviors": self.supporting_behaviors,
            "supporting_flows": self.supporting_flows,
            "confidence_breakdown": self.confidence_breakdown,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CandidateEvidence":
        """Deserializes a dictionary to a CandidateEvidence instance."""
        if not d:
            return cls()
        return cls(
            supporting_entities=list(d.get("supporting_entities", [])),
            supporting_relationships=list(d.get("supporting_relationships", [])),
            supporting_behaviors=list(d.get("supporting_behaviors", [])),
            supporting_flows=list(d.get("supporting_flows", [])),
            confidence_breakdown=dict(d.get("confidence_breakdown", {})),
        )
