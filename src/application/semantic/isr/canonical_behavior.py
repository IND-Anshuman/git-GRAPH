"""Intermediate Semantic Representation: CanonicalBehavior definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class BehaviorEvidence:
    """Audit trail of code targets and patterns supporting a behavior classification."""

    matched_imports: List[str] = field(default_factory=list)
    matched_calls: List[str] = field(default_factory=list)
    matched_heuristics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalBehavior:
    """Action signature matched against normalized registry mappings."""

    canonical_id: str
    matched_entity_id: str
    confidence: float
    evidence: BehaviorEvidence = field(default_factory=BehaviorEvidence)
