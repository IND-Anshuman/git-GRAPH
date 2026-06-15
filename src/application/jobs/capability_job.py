"""Job for executing capability mapping and staging capability candidates."""

import uuid
import re
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.entities.capability_candidate import CapabilityCandidate
from src.domain.value_objects.candidate_evidence import CandidateEvidence

class CapabilityJob:
    """Discovers macro technical/business capabilities based on repository code entities and logic signatures."""
    
    def __init__(self, uow_factory):
        self.uow_factory = uow_factory
        
    def run(self, repository_id: uuid.UUID) -> dict:
        repo_id = RepositoryId(repository_id)
        
        # 1. Fetch code entities and logic signatures
        with self.uow_factory() as uow:
            db_entities = uow.code_entities.get_by_repository(repo_id)
            db_signatures = uow.logic_signatures.list_by_repository(repo_id)
            
        # Group entities/signatures into capability domains
        capabilities_found = {}
        
        # Identity / Security
        iam_keywords = ["auth", "login", "signup", "permission", "rbac", "jwt", "token", "session", "bcrypt", "oauth", "credential"]
        # Payments
        payment_keywords = ["pay", "charge", "invoice", "wallet", "stripe", "billing", "checkout", "transaction", "ledger"]
        # Database / Storage
        db_keywords = ["database", "db", "query", "repository", "sql", "redis", "mongo", "postgres", "store", "persist"]
        # AI / ML
        ai_keywords = ["llm", "openai", "anthropic", "agent", "prompt", "chat", "model", "embed", "langchain"]
        
        def check_keywords(text: str, keywords: list) -> bool:
            text_lower = text.lower()
            return any(k in text_lower for k in keywords)
            
        for e in db_entities:
            e_name = e.name
            e_id = str(e.seid.value)
            
            if check_keywords(e_name, iam_keywords):
                capabilities_found.setdefault("Identity & Access Management", []).append(e_id)
            elif check_keywords(e_name, payment_keywords):
                capabilities_found.setdefault("Billing & Payment Processing", []).append(e_id)
            elif check_keywords(e_name, db_keywords):
                capabilities_found.setdefault("Data Storage & Persistence", []).append(e_id)
            elif check_keywords(e_name, ai_keywords):
                capabilities_found.setdefault("AI & Agent Integration", []).append(e_id)
                
        for s in db_signatures:
            s_name = s.canonical_name
            e_id = str(s.entity_seid) if hasattr(s, 'entity_seid') else ""
            if not e_id:
                continue
                
            if check_keywords(s_name, iam_keywords):
                capabilities_found.setdefault("Identity & Access Management", []).append(e_id)
            elif check_keywords(s_name, payment_keywords):
                capabilities_found.setdefault("Billing & Payment Processing", []).append(e_id)
            elif check_keywords(s_name, db_keywords):
                capabilities_found.setdefault("Data Storage & Persistence", []).append(e_id)
            elif check_keywords(s_name, ai_keywords):
                capabilities_found.setdefault("AI & Agent Integration", []).append(e_id)

        candidates = []
        with self.uow_factory() as uow:
            from src.infrastructure.persistence.models.capability_models import CapabilityCandidateModel
            from src.application.services.ingestion_pipeline import to_json_ready
            
            for cap_name, entities in capabilities_found.items():
                entities = list(set(entities))
                if not entities:
                    continue
                    
                # Generate deterministic UUID for capability
                cap_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"capability-candidate:{repository_id}:{cap_name}")
                
                # Confidence is proportional to number of supporting entities, max 0.95
                confidence = min(0.95, 0.50 + (len(entities) * 0.05))
                
                evidence = CandidateEvidence(
                    supporting_entities=entities,
                    supporting_relationships=[],
                    supporting_behaviors=[],
                    confidence_breakdown={"heuristic_match": confidence}
                )
                
                existing = uow._session.get(CapabilityCandidateModel, cap_id)
                if not existing:
                    model = CapabilityCandidateModel(
                        id=cap_id,
                        repository_id=repository_id,
                        name=cap_name,
                        confidence=confidence,
                        evidence=to_json_ready(evidence),
                        status="CANDIDATE"
                    )
                    uow._session.add(model)
                    candidates.append(model)
                    
            uow.commit()
            
        return {
            "capability_candidates_discovered": len(candidates)
        }
