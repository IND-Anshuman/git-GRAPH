"""Base extraction strategy interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType

from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.infrastructure.extraction.semantic_evidence_engine.raw_signal import RawSignal
from src.infrastructure.extraction.semantic_evidence_engine.raw_structure_signature import RawStructureSignature

@dataclass
class RawEntity:
    """Raw entity extracted from syntax tree before domain mapping."""
    name: str
    entity_type: EntityType
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    source_text: str
    parent_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    span: SourceSpan | None = None
    signals: List[RawSignal] = field(default_factory=list)
    structure_signature: RawStructureSignature | None = None

@dataclass
class RawRelationship:
    """Raw relationship extracted from syntax tree before domain mapping."""
    source_name: str
    target_name: str
    relationship_type: RelationshipType
    metadata: Dict[str, Any] = field(default_factory=dict)
    span: SourceSpan | None = None

class IExtractionStrategy(ABC):
    """Strategy interface for extracting entities and relationships."""
    
    @abstractmethod
    def extract_entities(self, tree: Any, source_code: str, file_path: str, module_name: str) -> List[RawEntity]:
        """Extract entities from the parsed tree."""
        pass
        
    @abstractmethod
    def extract_relationships(self, tree: Any, source_code: str, entities: List[RawEntity]) -> List[RawRelationship]:
        """Extract relationships from the parsed tree."""
        pass
