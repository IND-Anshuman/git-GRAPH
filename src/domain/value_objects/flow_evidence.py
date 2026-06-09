"""Value object representing evidence that supports a discovered flow path."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class FlowEvidence:
    """Grounding tokens supporting a discovered flow path validation."""

    entities: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this value object to a dictionary."""
        return {
            "entities": self.entities,
            "relationships": self.relationships,
            "behaviors": self.behaviors,
            "confidence_breakdown": self.confidence_breakdown,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FlowEvidence":
        """Deserializes a dictionary to a FlowEvidence instance."""
        if not d:
            return cls()
        return cls(
            entities=list(d.get("entities", [])),
            relationships=list(d.get("relationships", [])),
            behaviors=list(d.get("behaviors", [])),
            confidence_breakdown=dict(d.get("confidence_breakdown", {})),
        )
