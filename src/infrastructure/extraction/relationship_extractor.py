"""Service for extracting Relationship objects."""

import uuid
from typing import List, Any, Dict, Optional
from src.domain.entities.relationship import Relationship
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.source_file import SourceFile
from src.domain.value_objects.entity_id import SEID
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.strategy_registry import ExtractionStrategyRegistry

class RelationshipExtractorService:
    """Extracts Relationship objects using language-specific strategies."""
    
    def __init__(self, registry: LanguageRegistry):
        self._registry = registry
        self._strategy_registry = ExtractionStrategyRegistry()
        
    def extract(self, parsed_tree: Any, source_code: str, entities: List[CodeEntity], source_file: SourceFile, extraction_result: Optional[Any] = None) -> List[Relationship]:
        """Extracts relationships from a parsed AST.
        
        Args:
            parsed_tree: The tree-sitter AST
            source_code: The file's source code
            entities: List of CodeEntity objects previously extracted
            source_file: The domain SourceFile object
            extraction_result: Optional cached extraction result
            
        Returns:
            List of domain Relationship objects
        """
        strategy = self._strategy_registry.get(source_file.language)
        
        if not strategy:
            return []
            
        # Reconstruct RawEntity objects with accurate span coordinates, source text, and SourceSpan
        from src.infrastructure.extraction.strategies.base import RawEntity
        from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
        
        raw_entities = []
        for e in entities:
            metadata = e.metadata or {}
            start_byte = metadata.get("start_byte")
            end_byte = metadata.get("end_byte")
            span = None
            if start_byte is not None and end_byte is not None:
                span = SourceSpan(
                    start_byte=start_byte,
                    end_byte=end_byte,
                    start_line=metadata.get("start_line", e.location.start_line),
                    end_line=metadata.get("end_line", e.location.end_line),
                    start_column=metadata.get("start_column", e.location.start_column),
                    end_column=metadata.get("end_column", e.location.end_column),
                    file_path=e.location.file_path,
                )
            
            raw_ent = RawEntity(
                name=e.name,
                entity_type=e.entity_type,
                start_line=metadata.get("start_line", e.location.start_line),
                end_line=metadata.get("end_line", e.location.end_line),
                start_column=metadata.get("start_column", e.location.start_column),
                end_column=metadata.get("end_column", e.location.end_column),
                source_text=metadata.get("source_text", e.source_text or ""),
                parent_name=metadata.get("parent_name"),
                metadata=metadata,
                span=span,
            )
            raw_entities.append(raw_ent)
        
        raw_rels = strategy.extract_relationships(parsed_tree, source_code, raw_entities, extraction_result)
        
        # Build map for fast resolution
        name_to_seid: Dict[str, SEID] = {e.name: e.seid for e in entities}
        
        domain_rels = []
        seen_rels = set()
        for raw in raw_rels:
            source_seid = name_to_seid.get(raw.source_name)
            target_seid = name_to_seid.get(raw.target_name)
            
            # If we couldn't resolve locally, skip or handle external references (for Phase 2)
            # For Phase 1, we map what we can
            if source_seid and target_seid:
                rel_key = (source_seid, target_seid, raw.relationship_type)
                if rel_key in seen_rels:
                    continue
                seen_rels.add(rel_key)
                
                rel = Relationship(
                    id=uuid.uuid4(),
                    repository_id=source_file.repository_id,
                    relationship_type=raw.relationship_type,
                    source_seid=source_seid,
                    target_seid=target_seid,
                    confidence=1.0,
                    metadata=raw.metadata
                )
                domain_rels.append(rel)
                
        return domain_rels
