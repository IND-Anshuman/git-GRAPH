from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple
from src.domain.value_objects.intelligence_hints import SemanticHint, SemanticRole, CapabilityHint, ArchitectureHint
from src.domain.value_objects.relationship_confidence import RelationshipConfidence
from src.infrastructure.extraction.strategies.base import RawEntity, RawRelationship
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_relationship import CanonicalRelationship
from src.domain.value_objects.semantic_extraction_report import SemanticExtractionReport

@dataclass
class CompilerContext:
    """Shared state container passed sequentially through the 9 Semantic Compiler passes."""
    language: str
    source_code: str
    file_path: str
    project_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Pass 1 AST output
    raw_entities: List[RawEntity] = field(default_factory=list)
    raw_relationships: List[RawRelationship] = field(default_factory=list)
    
    # Pass 2 Framework output
    frameworks_detected: List[str] = field(default_factory=list)
    
    # Pass 3 Roles output
    inferred_roles: Dict[str, SemanticRole] = field(default_factory=dict)
    
    # Pass 4 Hints output
    semantic_hints: List[SemanticHint] = field(default_factory=list)
    
    # Pass 5 Relationships confidence output
    relationships_confidence: Dict[Tuple[str, str, str], RelationshipConfidence] = field(default_factory=dict)
    
    # Pass 6 Flow output
    flows: List[Any] = field(default_factory=list)  # List[CanonicalFlow]
    
    # Pass 7 Capability output
    capability_hints: List[CapabilityHint] = field(default_factory=list)
    
    # Pass 8 Architecture output
    architecture_hints: List[ArchitectureHint] = field(default_factory=list)
    
    # Misc
    imports: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    
    # SEEE extraction result
    extraction_result: Any = None
    
    # Pass 9 final output
    generated_entities: List[CanonicalEntity] = field(default_factory=list)
    generated_relationships: List[CanonicalRelationship] = field(default_factory=list)
    report: SemanticExtractionReport | None = None
