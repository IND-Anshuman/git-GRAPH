"""Job for executing concept discovery scan and staging concept candidates."""

import uuid
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.semantic.discovery.concept_discovery_engine import ConceptDiscoveryEngine
from src.domain.value_objects.repository_id import RepositoryId

class ConceptJob:
    """Discovers high-level semantic concepts, registers them, and persists candidates."""
    
    def __init__(self, concept_discovery_engine: ConceptDiscoveryEngine, uow_factory):
        self.concept_discovery_engine = concept_discovery_engine
        self.uow_factory = uow_factory
        
    def run(self, repository_id: uuid.UUID) -> dict:
        repo_id = RepositoryId(repository_id)
        
        # Run concept discovery scan
        candidates = self.concept_discovery_engine.discover_concept_candidates(repo_id)
        
        # Persist candidates to the database
        with self.uow_factory() as uow:
            from src.infrastructure.persistence.models.concept_models import ConceptCandidateModel
            from src.application.services.ingestion_pipeline import to_json_ready
            
            for c in candidates:
                # Add to DB session
                existing = uow._session.get(ConceptCandidateModel, c.id)
                if not existing:
                    model = ConceptCandidateModel(
                        id=c.id,
                        name=c.name,
                        confidence=c.confidence,
                        evidence=to_json_ready(c.evidence),
                        ontology_parent_candidate=c.ontology_parent_candidate,
                        status=c.status
                    )
                    uow._session.add(model)
            uow.commit()
            
        return {
            "concept_candidates_discovered": len(candidates)
        }
