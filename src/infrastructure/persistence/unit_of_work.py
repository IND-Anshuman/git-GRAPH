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
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is not None:
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

