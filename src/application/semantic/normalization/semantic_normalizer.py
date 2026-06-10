"""Translates parsed AST structures into Intermediate Semantic Representation (ISR)."""

import uuid
from typing import Any, Dict, List, Optional
from src.application.semantic.isr import (
    CanonicalEntity,
    CanonicalRelationship,
    CanonicalBehavior,
    BehaviorEvidence,
    CanonicalFlow,
)
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.normalization.normalization_rules import NormalizationRules
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine


class SemanticNormalizer:
    """Orchestrates signature mapping, generics matching, and flow construction."""

    def __init__(self, registry: CanonicalRegistry, type_engine: TypeResolutionEngine) -> None:
        self.registry = registry
        self.type_engine = type_engine

    def normalize_entity(self, raw_entity: Dict[str, Any], language: str) -> CanonicalEntity:
        """
        Converts raw parsed AST entity metadata to a CanonicalEntity.
        
        Args:
            raw_entity: Dictionary containing parsed AST attributes.
            language: Target language string.
            
        Returns:
            CanonicalEntity instance.
        """
        name = raw_entity.get("name", "")
        qualified_name = raw_entity.get("qualified_name", name)
        entity_type = raw_entity.get("type", "Class")

        # Resolve type parameters and generics
        resolved_type = self.type_engine.resolve_type(raw_entity.get("return_type", ""))

        entity_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{language}:{entity_type}:{qualified_name}"
        ))

        return CanonicalEntity(
            id=entity_id,
            name=name,
            qualified_name=qualified_name,
            entity_type=entity_type,
            visibility=raw_entity.get("visibility", "public"),
            return_type=resolved_type["normalized_base"],
            generics=resolved_type["generic_args"],
            decorators=raw_entity.get("decorators", []),
            location=raw_entity.get("location"),
            metadata=raw_entity.get("metadata", {}),
            semantic_type=raw_entity.get("semantic_type")
        )

    def normalize_relationship(
        self,
        from_entity: CanonicalEntity,
        to_entity: CanonicalEntity,
        rel_type: str,
        confidence: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        semantic_relationship_type: Optional[Any] = None
    ) -> CanonicalRelationship:
        """
        Creates a CanonicalRelationship edge between two entities.
        
        Args:
            from_entity: Source entity.
            to_entity: Destination entity.
            rel_type: Relationship code string.
            confidence: Extraction confidence value.
            properties: Additional relationship properties.
            semantic_relationship_type: Ontology semantic relationship type.
            
        Returns:
            CanonicalRelationship edge.
        """
        rel_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{from_entity.id}:{to_entity.id}:{rel_type}"
        ))
        return CanonicalRelationship(
            id=rel_id,
            from_entity_id=from_entity.id,
            to_entity_id=to_entity.id,
            relationship_type=rel_type,
            confidence=confidence,
            properties=properties or {},
            semantic_relationship_type=semantic_relationship_type
        )

    def map_behavior(self, entity: CanonicalEntity, imports: List[str], calls: List[str], language: str) -> Optional[CanonicalBehavior]:
        """
        Resolves a CanonicalBehavior by matching imports, calls, or heuristics.
        
        Args:
            entity: CanonicalEntity to map behavior onto.
            imports: Extracted imports list.
            calls: Extracted invocation calls.
            language: Programming language name.
            
        Returns:
            Optional CanonicalBehavior match.
        """
        norm_calls = [NormalizationRules.normalize_method_name(c) for c in calls]

        # 1. Exact pattern registry check
        for defn in self.registry.list_behaviors():
            for rule in defn.mappings:
                if rule.language.lower() == language.lower():
                    import_match = any(imp in imports for imp in rule.imports)
                    call_match = any(c in norm_calls or any(rc in c for rc in rule.calls) for c in calls)

                    if import_match or call_match:
                        evidence = BehaviorEvidence(
                            matched_imports=[imp for imp in rule.imports if imp in imports],
                            matched_calls=[c for c in rule.calls if any(c in rc for rc in calls)],
                            matched_heuristics={}
                        )
                        return CanonicalBehavior(
                            canonical_id=defn.id,
                            matched_entity_id=entity.id,
                            confidence=1.0 if (import_match and call_match) else 0.85,
                            evidence=evidence
                        )

        # 2. Structural heuristics matching fallback
        normalized_entity_name = NormalizationRules.normalize_method_name(entity.name)
        if "verify" in normalized_entity_name or "check" in normalized_entity_name:
            if "password" in normalized_entity_name or "pw" in normalized_entity_name:
                evidence = BehaviorEvidence(
                    matched_heuristics={"entity_name_match": True}
                )
                return CanonicalBehavior(
                    canonical_id="auth_password_verification",
                    matched_entity_id=entity.id,
                    confidence=0.70,
                    evidence=evidence
                )

        return None

    def trace_flow(self, flow_type: str, entities: List[CanonicalEntity], confidence: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> Optional[CanonicalFlow]:
        """
        Assembles ordered sequence of entities into a first-class flow path.
        
        Args:
            flow_type: Path type code.
            entities: Traversing entities in sequence.
            confidence: Path confidence score.
            metadata: Custom flow attributes.
            
        Returns:
            Optional CanonicalFlow entity.
        """
        if len(entities) < 2:
            return None

        source = entities[0]
        target = entities[-1]
        intermediates = [e.id for e in entities[1:-1]]

        flow_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{flow_type}:{source.id}:{target.id}:" + "-".join(intermediates)
        ))

        return CanonicalFlow(
            id=flow_id,
            flow_type=flow_type,
            source_entity_id=source.id,
            target_entity_id=target.id,
            intermediate_entities=intermediates,
            confidence=confidence,
            metadata=metadata or {}
        )
