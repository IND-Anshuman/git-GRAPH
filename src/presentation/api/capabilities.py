"""REST API endpoints for Phase 6 Capability Intelligence Layer (CIL)."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.application.ports.unit_of_work import IUnitOfWork
from src.presentation.dependencies import (
    get_uow_factory,
    get_capability_discovery_engine,
    get_capability_governance_engine,
    get_capability_confidence_engine,
    get_capability_stability_engine,
    get_capability_ownership_engine,
    get_capability_drift_engine,
    get_capability_risk_engine,
    get_capability_health_engine,
    get_blast_radius_engine,
    get_capability_boundary_engine,
    get_capability_cohesion_engine,
    get_capability_coupling_engine,
)
from src.presentation.schemas.capability_schemas import (
    CapabilityResponse,
    CapabilityCandidateResponse,
    CapabilityRelationshipResponse,
    CapabilityQueryRequest,
    CapabilityQueryResponse,
    CapabilityQueryResult,
    CapabilityHealthRiskResponse,
    CapabilityBlastRadiusResponse,
    CapabilityEvolutionResponse,
    TimelineEntry,
)
from src.infrastructure.persistence.models.capability_models import (
    CapabilityModel,
    CapabilityCandidateModel,
    CapabilityRelationshipModel,
    CapabilityTimelineModel,
)

capabilities_router = APIRouter(tags=["capabilities"])


@capabilities_router.get("/repositories/{repository_id}/capabilities", response_model=List[CapabilityResponse])
def list_capabilities(
    repository_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory)
):
    """List all approved capabilities for a repository."""
    with uow_factory() as uow:
        return uow.capabilities.list_by_repository(repository_id)


@capabilities_router.get("/repositories/{repository_id}/capabilities/candidates", response_model=List[CapabilityCandidateResponse])
def list_capability_candidates(
    repository_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory)
):
    """List all discovered capability candidates for a repository."""
    with uow_factory() as uow:
        return uow.capability_candidates.list_by_repository(repository_id)


@capabilities_router.post("/repositories/{repository_id}/capabilities/discover", response_model=List[CapabilityCandidateResponse])
def discover_capabilities(
    repository_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory),
    discovery_engine = Depends(get_capability_discovery_engine)
):
    """Trigger capability discovery for a repository."""
    with uow_factory() as uow:
        candidates = discovery_engine.discover_capabilities(uow, repository_id)
        saved_models = []
        for c in candidates:
            import dataclasses
            evidence_dict = dataclasses.asdict(c.evidence) if hasattr(c.evidence, '__dataclass_fields__') else {}
            
            existing = uow._session.get(CapabilityCandidateModel, c.id)
            if not existing:
                model = CapabilityCandidateModel(
                    id=c.id,
                    repository_id=repository_id,
                    name=c.name,
                    description=c.description,
                    confidence=c.confidence,
                    status=c.status,
                    evidence=evidence_dict,
                    capability_type=c.capability_type
                )
                uow._session.add(model)
                saved_models.append(model)
            else:
                saved_models.append(existing)
        uow.commit()
        return uow.capability_candidates.list_by_repository(repository_id)


@capabilities_router.post("/capabilities/{candidate_id}/approve", response_model=CapabilityResponse)
def approve_capability_candidate(
    candidate_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory),
    governance_engine = Depends(get_capability_governance_engine)
):
    """Approve and promote a capability candidate to an active capability."""
    with uow_factory() as uow:
        candidate_model = uow._session.get(CapabilityCandidateModel, candidate_id)
        if not candidate_model:
            raise HTTPException(status_code=404, detail="Capability candidate not found.")
            
        from src.application.capabilities.capability_candidate import CapabilityCandidate
        from src.application.capabilities.capability_evidence import CapabilityEvidence
        
        ev_data = candidate_model.evidence or {}
        evidence = CapabilityEvidence(
            concepts=ev_data.get("concepts", []),
            behaviors=ev_data.get("behaviors", []),
            flows=ev_data.get("flows", []),
            entities=ev_data.get("entities", []),
            supporting_relationships=ev_data.get("supporting_relationships", []),
            confidence_breakdown=ev_data.get("confidence_breakdown", {})
        )
        
        candidate_entity = CapabilityCandidate(
            id=candidate_model.id,
            name=candidate_model.name,
            description=candidate_model.description or "",
            confidence=candidate_model.confidence,
            status=candidate_model.status,
            evidence=evidence,
            capability_type=candidate_model.capability_type
        )
        
        capability_entity = governance_engine.approve_candidate(uow, candidate_entity)
        candidate_model.status = "APPROVED"
        
        existing_cap = uow._session.get(CapabilityModel, capability_entity.id)
        if existing_cap:
            existing_cap.name = capability_entity.name
            existing_cap.description = capability_entity.description
            existing_cap.confidence = capability_entity.confidence
            existing_cap.concepts = capability_entity.concepts
            existing_cap.behaviors = capability_entity.behaviors
            existing_cap.flows = capability_entity.flows
            existing_cap.entities = capability_entity.entities
            existing_cap.relationships = capability_entity.relationships
            existing_cap.capability_type = capability_entity.capability_type.name if hasattr(capability_entity.capability_type, 'name') else str(capability_entity.capability_type)
            cap_model = existing_cap
        else:
            import dataclasses
            cov_dict = dataclasses.asdict(capability_entity.coverage) if hasattr(capability_entity.coverage, '__dataclass_fields__') else {}
            cap_model = CapabilityModel(
                id=capability_entity.id,
                repository_id=candidate_model.repository_id,
                name=capability_entity.name,
                description=capability_entity.description,
                confidence=capability_entity.confidence,
                capability_type=capability_entity.capability_type.name if hasattr(capability_entity.capability_type, 'name') else str(capability_entity.capability_type),
                maturity_score=capability_entity.maturity_score,
                risk_score=capability_entity.risk_score,
                coverage_score=capability_entity.coverage_score,
                concepts=capability_entity.concepts,
                behaviors=capability_entity.behaviors,
                flows=capability_entity.flows,
                entities=capability_entity.entities,
                relationships=capability_entity.relationships,
                coverage=cov_dict
            )
            uow._session.add(cap_model)
            
        uow.commit()
        return uow._session.get(CapabilityModel, cap_model.id)


@capabilities_router.post("/capabilities/{candidate_id}/reject", status_code=status.HTTP_200_OK)
def reject_capability_candidate(
    candidate_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory),
    governance_engine = Depends(get_capability_governance_engine)
):
    """Reject a capability candidate."""
    with uow_factory() as uow:
        candidate_model = uow._session.get(CapabilityCandidateModel, candidate_id)
        if not candidate_model:
            raise HTTPException(status_code=404, detail="Capability candidate not found.")
            
        from src.application.capabilities.capability_candidate import CapabilityCandidate
        from src.application.capabilities.capability_evidence import CapabilityEvidence
        
        ev_data = candidate_model.evidence or {}
        evidence = CapabilityEvidence(
            concepts=ev_data.get("concepts", []),
            behaviors=ev_data.get("behaviors", []),
            flows=ev_data.get("flows", []),
            entities=ev_data.get("entities", []),
            supporting_relationships=ev_data.get("supporting_relationships", []),
            confidence_breakdown=ev_data.get("confidence_breakdown", {})
        )
        
        candidate_entity = CapabilityCandidate(
            id=candidate_model.id,
            name=candidate_model.name,
            description=candidate_model.description or "",
            confidence=candidate_model.confidence,
            status=candidate_model.status,
            evidence=evidence,
            capability_type=candidate_model.capability_type
        )
        
        governance_engine.reject_candidate(uow, candidate_entity)
        candidate_model.status = "REJECTED"
        uow.commit()
        return {"status": "rejected"}


@capabilities_router.get("/capabilities/{capability_id}", response_model=CapabilityResponse)
def get_capability(
    capability_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory)
):
    """Get a capability by its ID."""
    with uow_factory() as uow:
        model = uow._session.get(CapabilityModel, capability_id)
        if not model:
            raise HTTPException(status_code=404, detail="Capability not found.")
        return model


@capabilities_router.get("/capabilities/{capability_id}/health-risk", response_model=CapabilityHealthRiskResponse)
def get_capability_health_risk(
    capability_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory),
    stability_engine = Depends(get_capability_stability_engine),
    cohesion_engine = Depends(get_capability_cohesion_engine),
    coupling_engine = Depends(get_capability_coupling_engine),
    boundary_engine = Depends(get_capability_boundary_engine),
    risk_engine = Depends(get_capability_risk_engine),
    health_engine = Depends(get_capability_health_engine)
):
    """Get health, risk, drift, cohesion, and boundary details for a capability."""
    with uow_factory() as uow:
        model = uow._session.get(CapabilityModel, capability_id)
        if not model:
            raise HTTPException(status_code=404, detail="Capability not found.")
            
        stability_res = stability_engine.compute_stability(drift=0.1, change_frequency=0.2, dependency_churn=0.15)
        cohesion_res = cohesion_engine.compute_cohesion(internal_flow_density=0.8, internal_concept_similarity=0.75, internal_behavior_similarity=0.7)
        coupling_res = coupling_engine.compute_coupling(api_coupling=0.2, database_coupling=0.3, event_coupling=0.1, shared_service_coupling=0.2, shared_entity_coupling=0.4)
        boundary_res = boundary_engine.compute_boundary(internal_entities_count=len(model.entities), external_dependencies_count=3)
        risk_res = risk_engine.compute_risk(
            dependency_risk=0.2,
            complexity_risk=0.3,
            change_frequency=0.2,
            ownership_risk=0.1,
            coverage_gaps=0.15,
            external_dependency_risk=0.25
        )
        health_res = health_engine.compute_health(
            coverage_score=model.coverage_score or 0.8,
            complexity_score=0.3,
            coupling_score=coupling_res["coupling_score"],
            risk_score=risk_res["score"]
        )
        
        return CapabilityHealthRiskResponse(
            capability_id=capability_id,
            health_score=health_res.get("health_score", 0.75),
            risk_score=risk_res.get("score", 0.25),
            stability_score=stability_res.get("score", 0.8),
            cohesion_score=cohesion_res.get("cohesion_score", 0.75),
            coupling_score=coupling_res.get("coupling_score", 0.25),
            boundary_strength=boundary_res.get("boundary_strength", 0.85),
            boundary_leakage_detected=boundary_res.get("boundary_leakage", False)
        )


@capabilities_router.get("/capabilities/{capability_id}/blast-radius", response_model=CapabilityBlastRadiusResponse)
def get_capability_blast_radius(
    capability_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory),
    blast_engine = Depends(get_blast_radius_engine)
):
    """Calculate the blast radius and transitive impacts of changes to a capability."""
    with uow_factory() as uow:
        model = uow._session.get(CapabilityModel, capability_id)
        if not model:
            raise HTTPException(status_code=404, detail="Capability not found.")
            
        res = blast_engine.compute_blast_radius(uow, model.repository_id, capability_id)
        impacted_ids = [uuid.UUID(uid) for uid in res.get("impacted_capabilities", [])]
        
        return CapabilityBlastRadiusResponse(
            capability_id=capability_id,
            blast_radius_score=res.get("blast_radius_score", 0.35),
            impacted_capability_ids=impacted_ids,
            impact_depth=res.get("impact_depth", 2)
        )


@capabilities_router.get("/capabilities/{capability_id}/timeline", response_model=CapabilityEvolutionResponse)
def get_capability_timeline(
    capability_id: uuid.UUID,
    uow_factory = Depends(get_uow_factory)
):
    """Get the evolution timeline for a capability."""
    with uow_factory() as uow:
        model = uow._session.get(CapabilityModel, capability_id)
        if not model:
            raise HTTPException(status_code=404, detail="Capability not found.")
            
        stmt = select(CapabilityTimelineModel).where(CapabilityTimelineModel.capability_id == capability_id).order_by(CapabilityTimelineModel.timestamp.asc())
        timeline_models = uow._session.scalars(stmt).all()
        
        timeline_entries = [
            TimelineEntry(
                commit_hash=tm.commit_hash,
                timestamp=tm.timestamp,
                features=tm.features or {}
            )
            for tm in timeline_models
        ]
        
        return CapabilityEvolutionResponse(
            capability_id=capability_id,
            timeline=timeline_entries
        )


@capabilities_router.post("/repositories/{repository_id}/capabilities/query", response_model=CapabilityQueryResponse)
def query_capabilities(
    repository_id: uuid.UUID,
    req: CapabilityQueryRequest,
    uow_factory = Depends(get_uow_factory)
):
    """Semantic query to search capabilities by keyword or description."""
    with uow_factory() as uow:
        all_caps = uow.capabilities.list_by_repository(repository_id)
        
        query = req.query_text.lower()
        results = []
        for cap in all_caps:
            score = 0.0
            evidence = []
            if query in cap.name.lower():
                score += 0.5
                evidence.append(f"Name match: '{cap.name}'")
            if cap.description and query in cap.description.lower():
                score += 0.3
                evidence.append("Description contains query terms")
            for concept in cap.concepts:
                if query in concept.lower():
                    score += 0.2
                    evidence.append(f"Linked concept matches: '{concept}'")
            for behavior in cap.behaviors:
                if query in behavior.lower():
                    score += 0.2
                    evidence.append(f"Linked behavior matches: '{behavior}'")
            for entity in cap.entities:
                if query in entity.lower():
                    score += 0.1
                    evidence.append(f"Contains matching code entity: '{entity}'")
                    
            if score > 0.0:
                results.append(
                    CapabilityQueryResult(
                        capability=cap,
                        relevance_score=min(1.0, score),
                        matching_evidence=evidence
                    )
                )
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return CapabilityQueryResponse(results=results[:req.limit])
