from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class KnowledgeConfidence:
    """Standardized representation of knowledge confidence metrics and derivation history."""
    score: float
    source: str
    rules_applied: List[str] = field(default_factory=list)
