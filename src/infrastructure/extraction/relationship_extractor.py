"""Service for extracting Relationship objects."""

import uuid
from typing import List, Any, Dict
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
        
    def extract(self, parsed_tree: Any, source_code: str, entities: List[CodeEntity], source_file: SourceFile) -> List[Relationship]:
        """Extracts relationships from a parsed AST.
        
        Args:
            parsed_tree: The tree-sitter AST
            source_code: The file's source code
            entities: List of CodeEntity objects previously extracted
            source_file: The domain SourceFile object
            
        Returns:
            List of domain Relationship objects
        """
        strategy = self._strategy_registry.get(source_file.language)
        
        if not strategy:
            return []
            
        # We need raw entities to feed the strategy
        # Let's map CodeEntity back to something like RawEntity, but strategy just needs the AST and source
        # wait, strategy.extract_relationships needs entities to resolve names
        # Actually strategy signature: extract_relationships(tree, source_code, entities)
        # Let's just create mock RawEntities with names
        from src.infrastructure.extraction.strategies.base import RawEntity
        raw_entities = [RawEntity(name=e.name, entity_type=e.entity_type, start_line=0, end_line=0, start_column=0, end_column=0, source_text="") for e in entities]
        
        raw_rels = strategy.extract_relationships(parsed_tree, source_code, raw_entities)
        
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
