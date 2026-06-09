"""Value object representing evidence that supports a discovered relationship."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class RelationshipEvidence:
    """Grounding tokens supporting a discovered dynamic relationship edge."""

    matched_calls: List[str] = field(default_factory=list)
    matched_routes: List[str] = field(default_factory=list)
    matched_events: List[str] = field(default_factory=list)
    matched_types: List[str] = field(default_factory=list)
    matched_dataflows: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes value object to a dictionary."""
        return {
            "matched_calls": self.matched_calls,
            "matched_routes": self.matched_routes,
            "matched_events": self.matched_events,
            "matched_types": self.matched_types,
            "matched_dataflows": self.matched_dataflows,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RelationshipEvidence":
        """Deserializes dictionary to a RelationshipEvidence instance."""
        if not d:
            return cls()
        return cls(
            matched_calls=list(d.get("matched_calls", [])),
            matched_routes=list(d.get("matched_routes", [])),
            matched_events=list(d.get("matched_events", [])),
            matched_types=list(d.get("matched_types", [])),
            matched_dataflows=list(d.get("matched_dataflows", [])),
        )
