from abc import ABC, abstractmethod
from typing import Self
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
    IIntegrityRepository,
    ILogicSignatureRepository,
    ILogicVersionRepository,
    ILogicTransitionRepository,
    ILogicEvidenceRepository,
    ILogicExplanationRepository,
    IBehaviorDriftRepository,
    IBehaviorPatternRepository,
    ILogicClusterRepository,
    IOntologyNodeRepository,
    IConceptNodeRepository,
    IConceptVersionRepository,
    IConceptEvidenceRepository,
    IConceptRelationshipRepository,
    IConceptClusterRepository,
    IConceptExplanationRepository,
    IConceptMetricsRepository,
    IConceptEvolutionRepository,
    IConceptDriftRepository,
    IMetaTypeRepository,
    IMetaDefinitionRepository,
    IEmbeddingModelRepository,
    IEmbeddingVersionRepository,
)

class IUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @property
    @abstractmethod
    def repositories(self) -> IRepositoryRepository:
        pass

    @property
    @abstractmethod
    def source_files(self) -> ISourceFileRepository:
        pass

    @property
    @abstractmethod
    def code_entities(self) -> ICodeEntityRepository:
        pass

    @property
    @abstractmethod
    def relationships(self) -> IRelationshipRepository:
        pass

    @property
    @abstractmethod
    def commits(self) -> ICommitRepository:
        pass

    @property
    @abstractmethod
    def entity_versions(self) -> IEntityVersionRepository:
        pass

    @property
    @abstractmethod
    def relationship_versions(self) -> IRelationshipVersionRepository:
        pass

    @property
    @abstractmethod
    def change_events(self) -> IChangeEventRepository:
        pass

    @property
    @abstractmethod
    def snapshots(self) -> IRepositorySnapshotRepository:
        pass

    @property
    @abstractmethod
    def metrics(self) -> IMetricsRepository:
        pass

    @property
    @abstractmethod
    def integrity(self) -> IIntegrityRepository:
        pass

    @property
    @abstractmethod
    def logic_signatures(self) -> ILogicSignatureRepository:
        pass

    @property
    @abstractmethod
    def logic_versions(self) -> ILogicVersionRepository:
        pass

    @property
    @abstractmethod
    def logic_transitions(self) -> ILogicTransitionRepository:
        pass

    @property
    @abstractmethod
    def logic_evidence(self) -> ILogicEvidenceRepository:
        pass

    @property
    @abstractmethod
    def behavior_explanations(self) -> ILogicExplanationRepository:
        pass

    @property
    @abstractmethod
    def behavior_drift(self) -> IBehaviorDriftRepository:
        pass

    @property
    @abstractmethod
    def behavior_patterns(self) -> IBehaviorPatternRepository:
        pass

    @property
    @abstractmethod
    def logic_clusters(self) -> ILogicClusterRepository:
        pass

    @property
    @abstractmethod
    def ontology_nodes(self) -> IOntologyNodeRepository:
        pass

    @property
    @abstractmethod
    def concept_nodes(self) -> IConceptNodeRepository:
        pass

    @property
    @abstractmethod
    def concept_versions(self) -> IConceptVersionRepository:
        pass

    @property
    @abstractmethod
    def concept_relationships(self) -> IConceptRelationshipRepository:
        pass

    @property
    @abstractmethod
    def concept_evidence(self) -> IConceptEvidenceRepository:
        pass

    @property
    @abstractmethod
    def concept_clusters(self) -> IConceptClusterRepository:
        pass

    @property
    @abstractmethod
    def concept_explanations(self) -> IConceptExplanationRepository:
        pass

    @property
    @abstractmethod
    def concept_metrics(self) -> IConceptMetricsRepository:
        pass

    @property
    @abstractmethod
    def concept_evolution(self) -> IConceptEvolutionRepository:
        pass

    @property
    @abstractmethod
    def concept_drift(self) -> IConceptDriftRepository:
        pass

    @property
    @abstractmethod
    def meta_types(self) -> IMetaTypeRepository:
        pass

    @property
    @abstractmethod
    def meta_definitions(self) -> IMetaDefinitionRepository:
        pass

    @property
    @abstractmethod
    def embedding_models(self) -> IEmbeddingModelRepository:
        pass

    @property
    @abstractmethod
    def embedding_versions(self) -> IEmbeddingVersionRepository:
        pass


