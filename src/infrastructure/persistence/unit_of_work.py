"""SQLAlchemy implementation of Unit of Work."""

from typing import Any
from sqlalchemy.orm import Session

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.repositories import (
    IRepositoryRepository,
    ISourceFileRepository,
    ICodeEntityRepository,
    IRelationshipRepository,
    ICommitRepository,
    IEntityVersionRepository,
    IRelationshipVersionRepository,
    IChangeEventRepository,
    IRepositorySnapshotRepository,
    IMetricsRepository,
    IIntegrityRepository
)

from src.infrastructure.persistence.repositories.sa_repository_repo import SARepositoryRepository
from src.infrastructure.persistence.repositories.sa_source_file_repo import SASourceFileRepository
from src.infrastructure.persistence.repositories.sa_code_entity_repo import SACodeEntityRepository
from src.infrastructure.persistence.repositories.sa_relationship_repo import SARelationshipRepository
from src.infrastructure.persistence.repositories.sa_commit_repo import SACommitRepository
from src.infrastructure.persistence.repositories.sa_entity_version_repo import SAEntityVersionRepository
from src.infrastructure.persistence.repositories.sa_relationship_version_repo import SARelationshipVersionRepository
from src.infrastructure.persistence.repositories.sa_change_event_repo import SAChangeEventRepository
from src.infrastructure.persistence.repositories.sa_snapshot_repo import SARepositorySnapshotRepository
from src.infrastructure.persistence.repositories.sa_metrics_repo import SAMetricsRepository
from src.infrastructure.persistence.repositories.sa_integrity_repo import SAIntegrityRepository
from src.infrastructure.persistence.repositories.sa_logic_repositories import (
    SALogicSignatureRepository,
    SALogicVersionRepository,
    SALogicTransitionRepository,
    SALogicEvidenceRepository,
    SABehaviorExplanationRepository,
    SABehaviorDriftRepository,
    SABehaviorPatternRepository,
    SALogicClusterRepository,
    SAOntologyNodeRepository,
)
from src.infrastructure.persistence.repositories.sa_concept_repositories import (
    SAConceptNodeRepository,
    SAConceptVersionRepository,
    SAConceptEvidenceRepository,
    SAConceptRelationshipRepository,
    SAConceptClusterRepository,
    SAConceptExplanationRepository,
    SAConceptMetricsRepository,
    SAConceptEvolutionRepository,
    SAConceptDriftRepository,
)
from src.infrastructure.persistence.repositories.sa_meta_repositories import (
    SAMetaTypeRepository,
    SAMetaDefinitionRepository,
    SAEmbeddingModelRepository,
    SAEmbeddingVersionRepository,
)
from src.infrastructure.persistence.repositories.sa_knowledge_artifact_repo import SAKnowledgeArtifactRepository
from src.infrastructure.persistence.repositories.sa_resolution_repos import (
    SASymbolGraphRepository,
    SASymbolReferenceRepository,
    SAVariableFlowRepository,
    SACrossFileResolutionRepository,
    SAExternalDependencyRepository,
    SAAIEvidenceRepository,
    SARepositoryArchitectureGraphRepository,
    SAArchitectureRelationshipRepository,
    SARepositoryStructureGraphRepository,
    SACompilerOutputVersionRepository,
    SAReasoningArtifactRepository,
    SAKnowledgeDriftRepository,
    SAExternalKnowledgeReferenceRepository,
)
from src.infrastructure.persistence.repositories.sa_capability_repos import (
    SACapabilityRepository,
    SACapabilityCandidateRepository,
    SACapabilityRelationshipRepository,
    SACapabilityFingerprintRepository,
    SACapabilityEvolutionRepository,
    SACapabilityTimelineRepository,
    SACapabilityDependencyRepository,
    SACapabilityHealthRepository,
    SACapabilityBlastRadiusRepository,
    SACapabilityProvenanceRepository,
    SACapabilityConfidenceRepository,
    SACapabilityOverlapRepository,
    SACapabilityStabilityRepository,
    SACapabilitySnapshotRepository,
    SACapabilityBoundaryRepository,
    SACapabilityCohesionRepository,
    SACapabilityCouplingRepository,
    SACapabilityEmbeddingRepository,
    SACapabilityTaxonomyCandidateRepository,
)
from src.infrastructure.persistence.repositories.sa_architecture_repos import (
    SAArchitectureProfileRepository,
    SAArchitectureSnapshotRepository,
    SAArchitectureFitnessRepository,
    SAArchitectureViolationRepository,
    SAArchitectureInvariantRepository,
"""SQLAlchemy implementation of Unit of Work."""

from typing import Any
from sqlalchemy.orm import Session

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.repositories import (
    IRepositoryRepository,
    ISourceFileRepository,
    ICodeEntityRepository,
    IRelationshipRepository,
    ICommitRepository,
    IEntityVersionRepository,
    IRelationshipVersionRepository,
    IChangeEventRepository,
    IRepositorySnapshotRepository,
    IMetricsRepository,
    IIntegrityRepository
)

from src.infrastructure.persistence.repositories.sa_repository_repo import SARepositoryRepository
from src.infrastructure.persistence.repositories.sa_source_file_repo import SASourceFileRepository
from src.infrastructure.persistence.repositories.sa_code_entity_repo import SACodeEntityRepository
from src.infrastructure.persistence.repositories.sa_relationship_repo import SARelationshipRepository
from src.infrastructure.persistence.repositories.sa_commit_repo import SACommitRepository
from src.infrastructure.persistence.repositories.sa_entity_version_repo import SAEntityVersionRepository
from src.infrastructure.persistence.repositories.sa_relationship_version_repo import SARelationshipVersionRepository
from src.infrastructure.persistence.repositories.sa_change_event_repo import SAChangeEventRepository
from src.infrastructure.persistence.repositories.sa_snapshot_repo import SARepositorySnapshotRepository
from src.infrastructure.persistence.repositories.sa_metrics_repo import SAMetricsRepository
from src.infrastructure.persistence.repositories.sa_integrity_repo import SAIntegrityRepository
from src.infrastructure.persistence.repositories.sa_logic_repositories import (
    SALogicSignatureRepository,
    SALogicVersionRepository,
    SALogicTransitionRepository,
    SALogicEvidenceRepository,
    SABehaviorExplanationRepository,
    SABehaviorDriftRepository,
    SABehaviorPatternRepository,
    SALogicClusterRepository,
    SAOntologyNodeRepository,
)
from src.infrastructure.persistence.repositories.sa_concept_repositories import (
    SAConceptNodeRepository,
    SAConceptVersionRepository,
    SAConceptEvidenceRepository,
    SAConceptRelationshipRepository,
    SAConceptClusterRepository,
    SAConceptExplanationRepository,
    SAConceptMetricsRepository,
    SAConceptEvolutionRepository,
    SAConceptDriftRepository,
)
from src.infrastructure.persistence.repositories.sa_meta_repositories import (
    SAMetaTypeRepository,
    SAMetaDefinitionRepository,
    SAEmbeddingModelRepository,
    SAEmbeddingVersionRepository,
)
from src.infrastructure.persistence.repositories.sa_knowledge_artifact_repo import SAKnowledgeArtifactRepository
from src.infrastructure.persistence.repositories.sa_resolution_repos import (
    SASymbolGraphRepository,
    SASymbolReferenceRepository,
    SAVariableFlowRepository,
    SACrossFileResolutionRepository,
    SAExternalDependencyRepository,
    SAAIEvidenceRepository,
    SARepositoryArchitectureGraphRepository,
    SAArchitectureRelationshipRepository,
    SARepositoryStructureGraphRepository,
    SACompilerOutputVersionRepository,
    SAReasoningArtifactRepository,
    SAKnowledgeDriftRepository,
    SAExternalKnowledgeReferenceRepository,
)
from src.infrastructure.persistence.repositories.sa_capability_repos import (
    SACapabilityRepository,
    SACapabilityCandidateRepository,
    SACapabilityRelationshipRepository,
    SACapabilityFingerprintRepository,
    SACapabilityEvolutionRepository,
    SACapabilityTimelineRepository,
    SACapabilityDependencyRepository,
    SACapabilityHealthRepository,
    SACapabilityBlastRadiusRepository,
    SACapabilityProvenanceRepository,
    SACapabilityConfidenceRepository,
    SACapabilityOverlapRepository,
    SACapabilityStabilityRepository,
    SACapabilitySnapshotRepository,
    SACapabilityBoundaryRepository,
    SACapabilityCohesionRepository,
    SACapabilityCouplingRepository,
    SACapabilityEmbeddingRepository,
    SACapabilityTaxonomyCandidateRepository,
)
from src.infrastructure.persistence.repositories.sa_architecture_repos import (
    SAArchitectureProfileRepository,
    SAArchitectureSnapshotRepository,
    SAArchitectureFitnessRepository,
    SAArchitectureViolationRepository,
    SAArchitectureInvariantRepository,
    SAArchitectureDriftRepository,
    SAArchitectureTimelineRepository,
    SAArchitectureBenchmarkRepository,
    SAArchitectureSimilarityRepository,
    SAOwnershipProfileRepository,
    SARefactoringCandidateRepository,
    SAArchitectureRecommendationRepository,
)
from src.infrastructure.persistence.repositories.sa_decision_repos import (
    SADecisionRepository,
    SADecisionVersionRepository,
    SADecisionEvidenceRepository,
    SADecisionImpactRepository,
    SADecisionImpactTimelineRepository,
    SADecisionDependencyRepository,
    SADecisionConflictRepository,
    SADecisionFitnessRepository,
    SADecisionSnapshotRepository,
    SAIntentRepository,
    SAIntentRelationshipRepository,
    SARepositoryMemoryEventRepository,
    SACausalRelationshipRepository
)
from src.infrastructure.persistence.database import DatabaseEngine


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of the Unit of Work pattern."""

    def __init__(self, db_engine: DatabaseEngine) -> None:
        self._db_engine = db_engine
        self._session: Session = None
        
    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self._db_engine.session_factory()
        self._repositories = SARepositoryRepository(self._session)
        self._source_files = SASourceFileRepository(self._session)
        self._code_entities = SACodeEntityRepository(self._session)
        self._relationships = SARelationshipRepository(self._session)
        self._commits = SACommitRepository(self._session)
        self._entity_versions = SAEntityVersionRepository(self._session)
        self._relationship_versions = SARelationshipVersionRepository(self._session)
        self._change_events = SAChangeEventRepository(self._session)
        self._snapshots = SARepositorySnapshotRepository(self._session)
        self._metrics = SAMetricsRepository(self._session)
        self._integrity = SAIntegrityRepository(self._session)
        self._logic_signatures = SALogicSignatureRepository(self._session)
        self._logic_versions = SALogicVersionRepository(self._session)
        self._logic_transitions = SALogicTransitionRepository(self._session)
        self._logic_evidence = SALogicEvidenceRepository(self._session)
        self._behavior_explanations = SABehaviorExplanationRepository(self._session)
        self._behavior_drift = SABehaviorDriftRepository(self._session)
        self._behavior_patterns = SABehaviorPatternRepository(self._session)
        self._logic_clusters = SALogicClusterRepository(self._session)
        self._ontology_nodes = SAOntologyNodeRepository(self._session)
        self._concept_nodes = SAConceptNodeRepository(self._session)
        self._concept_versions = SAConceptVersionRepository(self._session)
        self._concept_relationships = SAConceptRelationshipRepository(self._session)
        self._concept_evidence = SAConceptEvidenceRepository(self._session)
        self._concept_clusters = SAConceptClusterRepository(self._session)
        self._concept_explanations = SAConceptExplanationRepository(self._session)
        self._concept_metrics = SAConceptMetricsRepository(self._session)
        self._concept_evolution = SAConceptEvolutionRepository(self._session)
        self._concept_drift = SAConceptDriftRepository(self._session)
        self._meta_types = SAMetaTypeRepository(self._session)
        self._meta_definitions = SAMetaDefinitionRepository(self._session)
        self._embedding_models = SAEmbeddingModelRepository(self._session)
        self._embedding_versions = SAEmbeddingVersionRepository(self._session)
        self._knowledge_artifacts = SAKnowledgeArtifactRepository(self._session)
        self._symbol_graph = SASymbolGraphRepository(self._session)
        self._symbol_references = SASymbolReferenceRepository(self._session)
        self._variable_flows = SAVariableFlowRepository(self._session)
        self._cross_file_resolutions = SACrossFileResolutionRepository(self._session)
        self._external_dependencies = SAExternalDependencyRepository(self._session)
        self._ai_evidences = SAAIEvidenceRepository(self._session)
        self._architecture_graphs = SARepositoryArchitectureGraphRepository(self._session)
        self._architecture_relationships = SAArchitectureRelationshipRepository(self._session)
        self._structure_graphs = SARepositoryStructureGraphRepository(self._session)
        self._compiler_output_versions = SACompilerOutputVersionRepository(self._session)
        self._reasoning_artifacts = SAReasoningArtifactRepository(self._session)
        self._knowledge_drifts = SAKnowledgeDriftRepository(self._session)
        self._external_knowledge_references = SAExternalKnowledgeReferenceRepository(self._session)
        self._capabilities = SACapabilityRepository(self._session)
        self._capability_candidates = SACapabilityCandidateRepository(self._session)
        self._capability_relationships = SACapabilityRelationshipRepository(self._session)
        self._capability_fingerprints = SACapabilityFingerprintRepository(self._session)
        self._capability_evolution = SACapabilityEvolutionRepository(self._session)
        self._capability_timelines = SACapabilityTimelineRepository(self._session)
        self._capability_dependencies = SACapabilityDependencyRepository(self._session)
        self._capability_health = SACapabilityHealthRepository(self._session)
        self._capability_blast_radius = SACapabilityBlastRadiusRepository(self._session)
        self._capability_provenance = SACapabilityProvenanceRepository(self._session)
        self._capability_confidence = SACapabilityConfidenceRepository(self._session)
        self._capability_overlap = SACapabilityOverlapRepository(self._session)
        self._capability_stability = SACapabilityStabilityRepository(self._session)
        self._capability_snapshots = SACapabilitySnapshotRepository(self._session)
        self._capability_boundaries = SACapabilityBoundaryRepository(self._session)
        self._capability_cohesion = SACapabilityCohesionRepository(self._session)
        self._capability_coupling = SACapabilityCouplingRepository(self._session)
        self._capability_embeddings = SACapabilityEmbeddingRepository(self._session)
        self._capability_taxonomy_candidates = SACapabilityTaxonomyCandidateRepository(self._session)
        self._architecture_profiles = SAArchitectureProfileRepository(self._session)
        self._architecture_snapshots = SAArchitectureSnapshotRepository(self._session)
        self._architecture_fitness = SAArchitectureFitnessRepository(self._session)
        self._architecture_violations = SAArchitectureViolationRepository(self._session)
        self._architecture_invariants = SAArchitectureInvariantRepository(self._session)
        self._architecture_drifts = SAArchitectureDriftRepository(self._session)
        self._architecture_timelines = SAArchitectureTimelineRepository(self._session)
        self._architecture_benchmarks = SAArchitectureBenchmarkRepository(self._session)
        self._architecture_similarities = SAArchitectureSimilarityRepository(self._session)
        self._ownership_profiles = SAOwnershipProfileRepository(self._session)
        self._refactoring_candidates = SARefactoringCandidateRepository(self._session)
        self._architecture_recommendations = SAArchitectureRecommendationRepository(self._session)
        self._decisions = SADecisionRepository(self._session)
        self._decision_versions = SADecisionVersionRepository(self._session)
        self._decision_evidence = SADecisionEvidenceRepository(self._session)
        self._decision_impacts = SADecisionImpactRepository(self._session)
        self._decision_impact_timelines = SADecisionImpactTimelineRepository(self._session)
        self._decision_dependencies = SADecisionDependencyRepository(self._session)
        self._decision_conflicts = SADecisionConflictRepository(self._session)
        self._decision_fitness = SADecisionFitnessRepository(self._session)
        self._decision_snapshots = SADecisionSnapshotRepository(self._session)
        self._intents = SAIntentRepository(self._session)
        self._intent_relationships = SAIntentRelationshipRepository(self._session)
        self._repository_memory_events = SARepositoryMemoryEventRepository(self._session)
        self._causal_relationships = SACausalRelationshipRepository(self._session)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
                import logging
                logging.getLogger(__name__).error(f"Unit of Work exception occurred, rolling back transaction: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
                self.rollback()
        finally:
            self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    @property
    def repositories(self) -> IRepositoryRepository:
        return self._repositories

    @property
    def source_files(self) -> ISourceFileRepository:
        return self._source_files

    @property
    def code_entities(self) -> ICodeEntityRepository:
        return self._code_entities

    @property
    def relationships(self) -> IRelationshipRepository:
        return self._relationships

    @property
    def commits(self) -> ICommitRepository:
        return self._commits

    @property
    def entity_versions(self) -> IEntityVersionRepository:
        return self._entity_versions

    @property
    def relationship_versions(self) -> IRelationshipVersionRepository:
        return self._relationship_versions

    @property
    def change_events(self) -> IChangeEventRepository:
        return self._change_events

    @property
    def snapshots(self) -> IRepositorySnapshotRepository:
        return self._snapshots

    @property
    def metrics(self) -> IMetricsRepository:
        return self._metrics

    @property
    def integrity(self) -> IIntegrityRepository:
        return self._integrity

    @property
    def logic_signatures(self):
        return self._logic_signatures

    @property
    def logic_versions(self):
        return self._logic_versions

    @property
    def logic_transitions(self):
        return self._logic_transitions

    @property
    def logic_evidence(self):
        return self._logic_evidence

    @property
    def behavior_explanations(self):
        return self._behavior_explanations

    @property
    def behavior_drift(self):
        return self._behavior_drift

    @property
    def behavior_patterns(self):
        return self._behavior_patterns

    @property
    def logic_clusters(self):
        return self._logic_clusters

    @property
    def ontology_nodes(self):
        return self._ontology_nodes

    @property
    def concept_nodes(self):
        return self._concept_nodes

    @property
    def concept_versions(self):
        return self._concept_versions

    @property
    def concept_relationships(self):
        return self._concept_relationships

    @property
    def concept_evidence(self):
        return self._concept_evidence

    @property
    def concept_clusters(self):
        return self._concept_clusters

    @property
    def concept_explanations(self):
        return self._concept_explanations

    @property
    def concept_metrics(self):
        return self._concept_metrics

    @property
    def concept_evolution(self):
        return self._concept_evolution

    @property
    def concept_drift(self):
        return self._concept_drift

    @property
    def meta_types(self):
        return self._meta_types

    @property
    def meta_definitions(self):
        return self._meta_definitions

    @property
    def embedding_models(self):
        return self._embedding_models

    @property
    def embedding_versions(self):
        return self._embedding_versions

    @property
    def knowledge_artifacts(self):
        return self._knowledge_artifacts

    @property
    def symbol_graph(self):
        return self._symbol_graph

    @property
    def symbol_references(self):
        return self._symbol_references

    @property
    def variable_flows(self):
        return self._variable_flows

    @property
    def cross_file_resolutions(self):
        return self._cross_file_resolutions

    @property
    def external_dependencies(self):
        return self._external_dependencies

    @property
    def ai_evidences(self):
        return self._ai_evidences

    @property
    def architecture_graphs(self):
        return self._architecture_graphs

    @property
    def architecture_relationships(self):
        return self._architecture_relationships

    @property
    def structure_graphs(self):
        return self._structure_graphs

    @property
    def compiler_output_versions(self):
        return self._compiler_output_versions

    @property
    def reasoning_artifacts(self):
        return self._reasoning_artifacts

    @property
    def knowledge_drifts(self):
        return self._knowledge_drifts

    @property
    def external_knowledge_references(self):
        return self._external_knowledge_references

    @property
    def capabilities(self):
        return self._capabilities

    @property
    def capability_candidates(self):
        return self._capability_candidates

    @property
    def capability_relationships(self):
        return self._capability_relationships

    @property
    def capability_fingerprints(self):
        return self._capability_fingerprints

    @property
    def capability_evolution(self):
        return self._capability_evolution

    @property
    def capability_timelines(self):
        return self._capability_timelines

    @property
    def capability_dependencies(self):
        return self._capability_dependencies

    @property
    def capability_health(self):
        return self._capability_health

    @property
    def capability_blast_radius(self):
        return self._capability_blast_radius

    @property
    def capability_provenance(self):
        return self._capability_provenance

    @property
    def capability_confidence(self):
        return self._capability_confidence

    @property
    def capability_overlap(self):
        return self._capability_overlap

    @property
    def capability_stability(self):
        return self._capability_stability

    @property
    def capability_snapshots(self):
        return self._capability_snapshots

    @property
    def capability_boundaries(self):
        return self._capability_boundaries

    @property
    def capability_cohesion(self):
        return self._capability_cohesion

    @property
    def capability_coupling(self):
        return self._capability_coupling

    @property
    def capability_embeddings(self):
        return self._capability_embeddings

    @property
    def capability_taxonomy_candidates(self):
        return self._capability_taxonomy_candidates

    @property
    def architecture_profiles(self):
        return self._architecture_profiles

    @property
    def architecture_snapshots(self):
        return self._architecture_snapshots

    @property
    def architecture_fitness(self):
        return self._architecture_fitness

    @property
    def architecture_violations(self):
        return self._architecture_violations

    @property
    def architecture_invariants(self):
        return self._architecture_invariants

    @property
    def architecture_drifts(self):
        return self._architecture_drifts

    @property
    def architecture_timelines(self):
        return self._architecture_timelines

    @property
    def architecture_benchmarks(self):
        return self._architecture_benchmarks

    @property
    def architecture_similarities(self):
        return self._architecture_similarities

    @property
    def ownership_profiles(self):
        return self._ownership_profiles

    @property
    def refactoring_candidates(self):
        return self._refactoring_candidates

    @property
    def architecture_recommendations(self):
        return self._architecture_recommendations

    @property
    def decisions(self):
        return self._decisions

    @property
    def decision_versions(self):
        return self._decision_versions

    @property
    def decision_evidence(self):
        return self._decision_evidence

    @property
    def decision_impacts(self):
        return self._decision_impacts

    @property
    def decision_impact_timelines(self):
        return self._decision_impact_timelines

    @property
    def decision_dependencies(self):
        return self._decision_dependencies

    @property
    def decision_conflicts(self):
        return self._decision_conflicts

    @property
    def decision_fitness(self):
        return self._decision_fitness

    @property
    def decision_snapshots(self):
        return self._decision_snapshots

    @property
    def intents(self):
        return self._intents

    @property
    def intent_relationships(self):
        return self._intent_relationships

    @property
    def repository_memory_events(self):
        return self._repository_memory_events

    @property
    def causal_relationships(self):
        return self._causal_relationships
