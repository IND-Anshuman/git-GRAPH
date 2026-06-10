from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class SemanticRole:
    """Inferred semantic purpose of an entity."""
    role_name: str
    confidence: float
    evidence: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class SemanticHint:
    """Fuzzy token/regex-based categorization hints."""
    category: str
    value: str
    confidence: float
    evidence: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class CapabilityHint:
    """High-level capability clustering (e.g. authentication, payment)."""
    capability: str
    confidence: float
    evidence: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ArchitectureHint:
    """Architectural pattern detection."""
    pattern: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
