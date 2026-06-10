from dataclasses import dataclass, field
from typing import Dict, List

@dataclass(frozen=True)
class SemanticExtractionReport:
    """Report generated after a successful 9-Pass compilation."""
    entities_found: int = 0
    relationships_found: int = 0
    hints_found: int = 0
    flows_found: int = 0
    roles_found: int = 0
    
    frameworks_detected: List[str] = field(default_factory=list)
    semantic_types_detected: List[str] = field(default_factory=list)
    
    capability_hints_found: int = 0
    architecture_hints_found: int = 0
    
    confidence_histogram: Dict[str, float] = field(default_factory=dict)
