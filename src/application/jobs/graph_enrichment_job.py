"""Job for dynamically discovering flows and couple-interaction edges (enrichment)."""

import uuid
from typing import List
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.semantic.discovery.flow_discovery_engine import FlowDiscoveryEngine
from src.application.semantic.discovery.relationship_discovery_engine import RelationshipDiscoveryEngine
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.relationship import Relationship
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_behavior import CanonicalBehavior, BehaviorEvidence

class GraphEnrichmentJob:
    """Enriches the graph with multi-hop execution flow sequences and interaction relationship links."""
    
    def __init__(self, uow_factory, calibration_engine: ConfidenceCalibrationEngine):
        self.uow_factory = uow_factory
        self.calibration_engine = calibration_engine
        
    def run(self, repository_id: uuid.UUID) -> dict:
        repo_id = RepositoryId(repository_id)
        
        # 1. Flow Discovery
        flow_engine = FlowDiscoveryEngine(self.uow_factory())
        flows = flow_engine.discover_flows(repo_id)
        
        # 2. Relationship Discovery
        discovered_rels: List[Relationship] = []
        with self.uow_factory() as uow:
            db_entities = uow.code_entities.get_by_repository(repo_id)
            db_signatures = uow.logic_signatures.list_by_repository(repo_id)
            
            entities = []
            for e in db_entities:
                entities.append(CanonicalEntity(
                    id=str(e.seid.value),
                    name=e.name,
                    qualified_name=e.qualified_name,
                    entity_type=e.entity_type.name if hasattr(e.entity_type, 'name') else str(e.entity_type),
                    location=e.location,
                    metadata=e.metadata
                ))
                
            behaviors = []
            for sig in db_signatures:
                behaviors.append(CanonicalBehavior(
                    canonical_id=sig.canonical_name,
                    matched_entity_id=str(sig.entity_seid) if hasattr(sig, 'entity_seid') else "",
                    confidence=getattr(sig, 'overall_confidence', 1.0),
                    evidence=BehaviorEvidence()
                ))
                
            engine = RelationshipDiscoveryEngine(uow, self.calibration_engine)
            discovered_rels = engine.discover_relationships(repo_id, entities, behaviors, flows)
            
            if discovered_rels:
                for r in discovered_rels:
                    r.metadata["layer"] = "BEHAVIOR"
                uow.relationships.save_batch(discovered_rels)
                uow.commit()
                
        return {
            "flows_discovered": len(flows),
            "relationships_discovered": len(discovered_rels)
        }
