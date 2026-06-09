"""REST API endpoints for Phase 4.75 Meta-Ontology, Schema Registry, and Discovery."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.value_objects.repository_id import RepositoryId
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.governance.governance_manager import GovernanceManager
from src.application.semantic.discovery import (
    EntityDiscoveryEngine,
    RelationshipDiscoveryEngine,
    BehaviorDiscoveryEngine,
    ConceptDiscoveryEngine,
    FlowDiscoveryEngine,
)
from src.application.semantic.evolution import SemanticEvolutionEngine
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.presentation.dependencies import (
    get_embedding_registry,
    get_schema_registry,
    get_governance_manager,
    get_entity_discovery_engine,
    get_relationship_discovery_engine,
    get_behavior_discovery_engine,
    get_concept_discovery_engine,
    get_flow_discovery_engine,
    get_semantic_evolution_engine,
    get_semantic_normalizer,
    get_uow_factory,
)
from src.presentation.schemas.meta_schemas import (
    MetaTypeSchema,
    MetaDefinitionSchema,
    EmbeddingModelSchema,
    EmbeddingVersionSchema,
    RegisterModelRequest,
    RegisterVersionRequest,
    RegisterTypeRequest,
    RegisterDefinitionRequest,
    DiscoveryResponse,
    PromotionApprovalRequest,
    DiscoveredCandidateSchema,
    ConceptCandidateSchema,
    CanonicalFlowSchema,
    EvolutionDiffSchema,
)
from src.presentation.schemas.responses import RelationshipSchema

meta_router = APIRouter(prefix="/meta", tags=["meta"])


@meta_router.post("/embeddings/models", response_model=EmbeddingModelSchema, status_code=status.HTTP_201_CREATED)
def register_embedding_model(
    payload: RegisterModelRequest,
    registry: EmbeddingRegistry = Depends(get_embedding_registry),
):
    """Registers a new embedding model configuration."""
    try:
        model = registry.register_model(
            model_id=payload.id,
            model_name=payload.model_name,
            provider=payload.provider,
            dimensions=payload.dimensions,
            distance_metric=payload.distance_metric,
            is_active=payload.is_active,
        )
        return model
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/embeddings/models/{model_id}/versions", response_model=EmbeddingVersionSchema, status_code=status.HTTP_201_CREATED)
def register_embedding_version(
    model_id: str,
    payload: RegisterVersionRequest,
    registry: EmbeddingRegistry = Depends(get_embedding_registry),
):
    """Registers a config version for an embedding model."""
    try:
        version = registry.register_version(
            model_id=model_id,
            version_string=payload.version_string,
            configuration=payload.configuration,
        )
        return version
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/embeddings/models/{model_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
def activate_embedding_model(
    model_id: str,
    registry: EmbeddingRegistry = Depends(get_embedding_registry),
):
    """Sets an embedding model as active and deactivates others."""
    try:
        registry.activate_model(model_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@meta_router.get("/embeddings/active", response_model=EmbeddingModelSchema)
def get_active_embedding_model(
    registry: EmbeddingRegistry = Depends(get_embedding_registry),
):
    """Retrieves the currently active embedding model configuration."""
    model = registry.get_active_model()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active embedding model registered.")
    return model


@meta_router.post("/types", response_model=MetaTypeSchema, status_code=status.HTTP_201_CREATED)
def register_meta_type(
    payload: RegisterTypeRequest,
    registry: SchemaRegistry = Depends(get_schema_registry),
):
    """Registers a new MetaType structure identifier."""
    try:
        meta_type = registry.register_type(
            type_id=payload.id,
            name=payload.name,
            category=payload.category,
            status=payload.status,
        )
        return meta_type
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/types/{type_id}/definitions", response_model=MetaDefinitionSchema, status_code=status.HTTP_201_CREATED)
def register_schema_definition(
    type_id: str,
    payload: RegisterDefinitionRequest,
    registry: SchemaRegistry = Depends(get_schema_registry),
):
    """Registers a new versioned schema definition schema configuration for a MetaType."""
    try:
        meta_def = registry.register_definition(
            type_id=type_id,
            schema_definition=payload.schema_definition,
            semantic_signature=payload.semantic_signature,
            version_string=payload.version_string,
        )
        return meta_def
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/types/{type_id}/validate")
def validate_instance_data(
    type_id: str,
    payload: dict,
    registry: SchemaRegistry = Depends(get_schema_registry),
):
    """Validates an instance dictionary against the latest schema of the target MetaType."""
    valid, err = registry.validate_instance(type_id, payload)
    if not valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
    return {"valid": True}


@meta_router.get("/types", response_model=List[MetaTypeSchema])
def list_meta_types(
    category: Optional[str] = None,
    registry: SchemaRegistry = Depends(get_schema_registry),
):
    """Lists registered MetaTypes, optionally filtered by category."""
    with registry.uow:
        if category:
            return registry.uow.meta_types.list_by_category(category)
        return registry.uow.meta_types.list_all()


@meta_router.post("/types/{type_id}/request-candidate")
def request_promotion_to_candidate(
    type_id: str,
    gov_manager: GovernanceManager = Depends(get_governance_manager),
):
    """Validates thresholds to promote a MetaType from EXPERIMENTAL to CANDIDATE."""
    success, msg = gov_manager.request_promotion_to_candidate(type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg}


@meta_router.post("/types/{type_id}/approve-active")
def approve_promotion_to_active(
    type_id: str,
    payload: PromotionApprovalRequest,
    gov_manager: GovernanceManager = Depends(get_governance_manager),
):
    """Admin/Human-in-the-loop approval to transition MetaType from CANDIDATE to ACTIVE."""
    success, msg = gov_manager.approve_promotion_to_active(type_id, payload.approver)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg}


@meta_router.post("/types/{type_id}/deprecate")
def deprecate_meta_type(
    type_id: str,
    gov_manager: GovernanceManager = Depends(get_governance_manager),
):
    """Transitions a MetaType status to DEPRECATED."""
    success, msg = gov_manager.deprecate_type(type_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    return {"message": msg}


@meta_router.post("/discovery/run", response_model=DiscoveryResponse)
def run_semantic_discovery(
    repository_id: str,
    similarity_threshold: float = 0.85,
    engine: EntityDiscoveryEngine = Depends(get_entity_discovery_engine),
):
    """Triggers EntityDiscoveryEngine dynamic clustering scan across a repository."""
    candidates = engine.discover_semantic_types(
        repository_id=RepositoryId.from_string(repository_id),
        similarity_threshold=similarity_threshold,
    )
    
    resp_candidates = []
    for mt, md in candidates:
        resp_candidates.append(
            DiscoveredCandidateSchema(
                meta_type=MetaTypeSchema.model_validate(mt),
                definition=MetaDefinitionSchema.model_validate(md),
            )
        )
    return DiscoveryResponse(candidates=resp_candidates)


@meta_router.post("/discovery/relationships", response_model=List[RelationshipSchema])
def discover_relationships(
    repository_id: str,
    engine: RelationshipDiscoveryEngine = Depends(get_relationship_discovery_engine),
    normalizer: SemanticNormalizer = Depends(get_semantic_normalizer),
    uow: SQLAlchemyUnitOfWork = Depends(get_uow_factory),
):
    """Triggers RelationshipDiscoveryEngine dynamic coupling scan across a repository."""
    repo_uuid = RepositoryId.from_string(repository_id)
    with uow:
        db_entities = uow.code_entities.get_by_repository(repo_uuid)

        canonical_entities = []
        for de in db_entities:
            raw_entity = {
                "name": de.name,
                "qualified_name": de.qualified_name,
                "type": de.entity_type.value if hasattr(de.entity_type, "value") else str(de.entity_type),
                "return_type": de.metadata.get("return_type", ""),
                "visibility": de.metadata.get("visibility", "public"),
                "decorators": de.metadata.get("decorators", []),
                "location": de.location,
                "metadata": de.metadata,
            }
            canonical_entities.append(
                normalizer.normalize_entity(
                    raw_entity,
                    de.language.value if hasattr(de.language, "value") else str(de.language),
                )
            )

        # Map behaviors
        behaviors = []
        for ce in canonical_entities:
            imports = ce.metadata.get("imports", [])
            calls = ce.metadata.get("calls", [])
            language = ce.metadata.get("language", "python")
            bh = normalizer.map_behavior(ce, imports, calls, language)
            if bh:
                behaviors.append(bh)

        # Map dynamic flows
        flows = []
        for ce in canonical_entities:
            flow_meta = ce.metadata.get("flows", [])
            for fm in flow_meta:
                flow_entities = []
                for entity_id in [ce.id] + fm.get("intermediate_entities", []) + [fm.get("target_entity_id")]:
                    found = next(
                        (e for e in canonical_entities if e.id == entity_id or e.name == entity_id),
                        None,
                    )
                    if found:
                        flow_entities.append(found)
                if len(flow_entities) >= 2:
                    fl = normalizer.trace_flow(
                        flow_type=fm.get("flow_type", "DATA"),
                        entities=flow_entities,
                        confidence=fm.get("confidence", 1.0),
                        metadata=fm.get("metadata", {}),
                    )
                    if fl:
                        flows.append(fl)

    relationships = engine.discover_relationships(
        repository_id=repo_uuid,
        entities=canonical_entities,
        behaviors=behaviors,
        flows=flows,
    )

    resp_rels = []
    for rel in relationships:
        resp_rels.append(
            RelationshipSchema(
                id=str(rel.id),
                relationship_type=rel.relationship_type.name
                if hasattr(rel.relationship_type, "name")
                else str(rel.relationship_type),
                source_seid=str(rel.source_seid.value),
                target_seid=str(rel.target_seid.value),
                source_name=rel.metadata.get("source_name", ""),
                target_name=rel.metadata.get("target_name", ""),
                confidence=rel.confidence,
                metadata=rel.metadata,
            )
        )
    return resp_rels


@meta_router.post("/discovery/behaviors", response_model=DiscoveryResponse)
def discover_behavior_patterns(
    repository_id: str,
    similarity_threshold: float = 0.85,
    engine: BehaviorDiscoveryEngine = Depends(get_behavior_discovery_engine),
    normalizer: SemanticNormalizer = Depends(get_semantic_normalizer),
    uow: SQLAlchemyUnitOfWork = Depends(get_uow_factory),
):
    """Triggers BehaviorDiscoveryEngine dynamic clustering scan across a repository."""
    repo_uuid = RepositoryId.from_string(repository_id)
    with uow:
        db_entities = uow.code_entities.get_by_repository(repo_uuid)

        canonical_entities = []
        for de in db_entities:
            raw_entity = {
                "name": de.name,
                "qualified_name": de.qualified_name,
                "type": de.entity_type.value if hasattr(de.entity_type, "value") else str(de.entity_type),
                "return_type": de.metadata.get("return_type", ""),
                "visibility": de.metadata.get("visibility", "public"),
                "decorators": de.metadata.get("decorators", []),
                "location": de.location,
                "metadata": de.metadata,
            }
            canonical_entities.append(
                normalizer.normalize_entity(
                    raw_entity,
                    de.language.value if hasattr(de.language, "value") else str(de.language),
                )
            )

    candidates = engine.discover_behavior_clusters(
        repository_id=repo_uuid,
        entities=canonical_entities,
        similarity_threshold=similarity_threshold,
    )

    resp_candidates = []
    for mt, md in candidates:
        resp_candidates.append(
            DiscoveredCandidateSchema(
                meta_type=MetaTypeSchema.model_validate(mt),
                definition=MetaDefinitionSchema.model_validate(md),
            )
        )
    return DiscoveryResponse(candidates=resp_candidates)


@meta_router.post("/discovery/concepts", response_model=List[ConceptCandidateSchema])
def discover_concepts(
    repository_id: str,
    similarity_threshold: float = 0.80,
    engine: ConceptDiscoveryEngine = Depends(get_concept_discovery_engine),
):
    """Triggers ConceptDiscoveryEngine dynamic clustering scan and stages candidates."""
    try:
        candidates = engine.discover_concept_candidates(
            repository_id=RepositoryId.from_string(repository_id),
            similarity_threshold=similarity_threshold,
        )
        return candidates
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/discovery/flows", response_model=List[CanonicalFlowSchema])
def discover_flows(
    repository_id: str,
    engine: FlowDiscoveryEngine = Depends(get_flow_discovery_engine),
):
    """Triggers FlowDiscoveryEngine dynamic multi-hop trace across a repository."""
    try:
        flows = engine.discover_flows(
            repository_id=RepositoryId.from_string(repository_id),
        )
        return flows
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.post("/governance/candidates/{id}/approve")
def approve_concept_candidate(
    id: str,
    payload: PromotionApprovalRequest,
    gov_manager: GovernanceManager = Depends(get_governance_manager),
):
    """Promotes a ConceptCandidate/MetaType to active ConceptNode."""
    success, msg = gov_manager.approve_promotion_to_active(
        type_id=id,
        approver_name=payload.approver,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"message": msg}


@meta_router.get("/evolution/graph", response_model=Dict[str, Any])
def get_evolution_graph(
    repository_id: str,
    commit_hash: str,
    engine: SemanticEvolutionEngine = Depends(get_semantic_evolution_engine),
):
    """Reconstructs structural, behavioral, and conceptual graph snapshots for a given commit."""
    try:
        snapshot = engine.graph_at_commit(
            repository_id=RepositoryId.from_string(repository_id),
            commit_hash=commit_hash,
        )
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@meta_router.get("/evolution/diff", response_model=Dict[str, Any])
def get_evolution_diff(
    repository_id: str,
    commit_a: str,
    commit_b: str,
    engine: SemanticEvolutionEngine = Depends(get_semantic_evolution_engine),
):
    """Computes structural and taxonomic additions/removals between two commits."""
    try:
        diff = engine.graph_diff(
            repository_id=RepositoryId.from_string(repository_id),
            commit_a=commit_a,
            commit_b=commit_b,
        )
        return diff
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

