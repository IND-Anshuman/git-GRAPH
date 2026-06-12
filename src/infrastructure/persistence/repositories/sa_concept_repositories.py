"""SQLAlchemy implementations of Phase 4 repositories."""

from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import Session

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_cluster import ConceptCluster
from src.domain.entities.concept_explanation import ConceptExplanation
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.entities.concept_metrics import ConceptMetrics
from src.domain.entities.concept_drift import ConceptDrift
from src.domain.value_objects.repository_id import RepositoryId

from src.domain.repositories.concept_repositories import (
    IConceptNodeRepository,
    IConceptVersionRepository,
    IConceptEvidenceRepository,
    IConceptRelationshipRepository,
    IConceptClusterRepository,
    IConceptExplanationRepository,
    IConceptMetricsRepository,
    IConceptEvolutionRepository,
    IConceptDriftRepository,
)

from src.infrastructure.persistence.mappers.concept_mapper import ConceptMapper
from src.infrastructure.persistence.models.concept_models import (
    ConceptNodeModel,
    ConceptVersionModel,
    ConceptEvidenceModel,
    ConceptRelationshipModel,
    ConceptClusterModel,
    ConceptClusterMemberModel,
    ConceptExplanationModel,
    ConceptMetricsModel,
    ConceptEvolutionModel,
    ConceptDriftModel,
)


class SAConceptNodeRepository(IConceptNodeRepository):
    """SQLAlchemy repository for ConceptNode entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, node: ConceptNode) -> None:
        model = ConceptMapper.to_concept_node_model(node)
        self.session.merge(model)

    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptNode]:
        model = self.session.get(ConceptNodeModel, id)
        return ConceptMapper.to_concept_node_entity(model) if model else None

    def get_by_ontology_node(self, repository_id: RepositoryId, ontology_node_id: str) -> Optional[ConceptNode]:
        stmt = select(ConceptNodeModel).where(
            and_(
                ConceptNodeModel.repository_id == repository_id.value,
                ConceptNodeModel.ontology_node_id == ontology_node_id,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_node_entity(model) if model else None

    def list_by_repository(self, repository_id: RepositoryId) -> List[ConceptNode]:
        stmt = select(ConceptNodeModel).where(
            ConceptNodeModel.repository_id == repository_id.value
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_node_entity(m) for m in models]

    def delete_by_repository(self, repository_id: RepositoryId) -> None:
        stmt = delete(ConceptNodeModel).where(
            ConceptNodeModel.repository_id == repository_id.value
        )
        self.session.execute(stmt)


class SAConceptVersionRepository(IConceptVersionRepository):
    """SQLAlchemy repository for ConceptVersion entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, version: ConceptVersion) -> None:
        model = ConceptMapper.to_concept_version_model(version)
        self.session.merge(model)

    def save_batch(self, versions: List[ConceptVersion]) -> None:
        for v in versions:
            self.save(v)

    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptVersion]:
        model = self.session.get(ConceptVersionModel, id)
        return ConceptMapper.to_concept_version_entity(model) if model else None

    def get_by_concept_at_commit(self, concept_id: uuid.UUID, commit_hash: str) -> Optional[ConceptVersion]:
        stmt = select(ConceptVersionModel).where(
            and_(
                ConceptVersionModel.concept_id == concept_id,
                ConceptVersionModel.commit_hash == commit_hash,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_version_entity(model) if model else None

    def list_by_concept(self, concept_id: uuid.UUID) -> List[ConceptVersion]:
        stmt = select(ConceptVersionModel).where(
            ConceptVersionModel.concept_id == concept_id
        ).order_by(ConceptVersionModel.version_number.asc())
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_version_entity(m) for m in models]

    def list_by_commit(self, commit_hash: str) -> List[ConceptVersion]:
        stmt = select(ConceptVersionModel).where(
            ConceptVersionModel.commit_hash == commit_hash
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_version_entity(m) for m in models]


class SAConceptEvidenceRepository(IConceptEvidenceRepository):
    """SQLAlchemy repository for ConceptEvidence entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_batch(self, evidence_list: List[ConceptEvidence]) -> None:
        for ev in evidence_list:
            model = ConceptMapper.to_concept_evidence_model(ev)
            self.session.merge(model)

    def list_by_concept_version(self, concept_version_id: uuid.UUID) -> List[ConceptEvidence]:
        stmt = select(ConceptEvidenceModel).where(
            ConceptEvidenceModel.concept_version_id == concept_version_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_evidence_entity(m) for m in models]

    def delete_by_concept_version(self, concept_version_id: uuid.UUID) -> None:
        stmt = delete(ConceptEvidenceModel).where(
            ConceptEvidenceModel.concept_version_id == concept_version_id
        )
        self.session.execute(stmt)


class SAConceptRelationshipRepository(IConceptRelationshipRepository):
    """SQLAlchemy repository for ConceptRelationship entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, relationship: ConceptRelationship) -> None:
        model = ConceptMapper.to_concept_relationship_model(relationship)
        self.session.merge(model)

    def save_batch(self, relationships: List[ConceptRelationship]) -> None:
        for r in relationships:
            self.save(r)

    def list_by_commit(self, commit_hash: str) -> List[ConceptRelationship]:
        stmt = select(ConceptRelationshipModel).where(
            ConceptRelationshipModel.commit_hash == commit_hash
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_relationship_entity(m) for m in models]

    def delete_by_commit(self, repository_id: RepositoryId, commit_hash: str) -> None:
        stmt = delete(ConceptRelationshipModel).where(
            and_(
                ConceptRelationshipModel.repository_id == repository_id.value,
                ConceptRelationshipModel.commit_hash == commit_hash,
            )
        )
        self.session.execute(stmt)


class SAConceptClusterRepository(IConceptClusterRepository):
    """SQLAlchemy repository for ConceptCluster entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, cluster: ConceptCluster) -> None:
        model = ConceptMapper.to_concept_cluster_model(cluster)
        self.session.merge(model)

    def get_by_id(self, id: uuid.UUID) -> Optional[ConceptCluster]:
        model = self.session.get(ConceptClusterModel, id)
        return ConceptMapper.to_concept_cluster_entity(model) if model else None

    def get_by_key(self, cluster_key: str) -> Optional[ConceptCluster]:
        stmt = select(ConceptClusterModel).where(ConceptClusterModel.cluster_key == cluster_key)
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_cluster_entity(model) if model else None

    def list_all(self) -> List[ConceptCluster]:
        stmt = select(ConceptClusterModel)
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_cluster_entity(m) for m in models]

    def add_member(self, cluster_id: uuid.UUID, concept_id: uuid.UUID) -> None:
        model = ConceptClusterMemberModel(
            id=uuid.uuid4(),
            cluster_id=cluster_id,
            concept_id=concept_id,
        )
        self.session.merge(model)
        # Update member count
        self.session.execute(
            update(ConceptClusterModel)
            .where(ConceptClusterModel.id == cluster_id)
            .values(member_count=ConceptClusterModel.member_count + 1)
        )

    def remove_member(self, cluster_id: uuid.UUID, concept_id: uuid.UUID) -> None:
        stmt = delete(ConceptClusterMemberModel).where(
            and_(
                ConceptClusterMemberModel.cluster_id == cluster_id,
                ConceptClusterMemberModel.concept_id == concept_id,
            )
        )
        self.session.execute(stmt)
        # Update member count
        self.session.execute(
            update(ConceptClusterModel)
            .where(ConceptClusterModel.id == cluster_id)
            .values(member_count=ConceptClusterModel.member_count - 1)
        )

    def get_concept_memberships(self, concept_id: uuid.UUID) -> List[ConceptCluster]:
        stmt = (
            select(ConceptClusterModel)
            .join(ConceptClusterMemberModel, ConceptClusterModel.id == ConceptClusterMemberModel.cluster_id)
            .where(ConceptClusterMemberModel.concept_id == concept_id)
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_cluster_entity(m) for m in models]

    def delete_all(self) -> None:
        self.session.execute(delete(ConceptClusterMemberModel))
        self.session.execute(delete(ConceptClusterModel))


class SAConceptExplanationRepository(IConceptExplanationRepository):
    """SQLAlchemy repository for ConceptExplanation entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, explanation: ConceptExplanation) -> None:
        model = ConceptMapper.to_concept_explanation_model(explanation)
        self.session.merge(model)

    def get_by_concept_version(self, concept_version_id: uuid.UUID) -> Optional[ConceptExplanation]:
        stmt = select(ConceptExplanationModel).where(ConceptExplanationModel.concept_version_id == concept_version_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_explanation_entity(model) if model else None


class SAConceptMetricsRepository(IConceptMetricsRepository):
    """SQLAlchemy repository for ConceptMetrics entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, metrics: ConceptMetrics) -> None:
        model = ConceptMapper.to_concept_metrics_model(metrics)
        self.session.merge(model)

    def save_batch(self, metrics_list: List[ConceptMetrics]) -> None:
        for m in metrics_list:
            self.save(m)

    def get_by_concept_version(self, concept_version_id: uuid.UUID) -> Optional[ConceptMetrics]:
        stmt = select(ConceptMetricsModel).where(ConceptMetricsModel.concept_version_id == concept_version_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_metrics_entity(model) if model else None


class SAConceptEvolutionRepository(IConceptEvolutionRepository):
    """SQLAlchemy repository for ConceptEvolution entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, evolution: ConceptEvolution) -> None:
        model = ConceptMapper.to_concept_evolution_model(evolution)
        self.session.merge(model)

    def save_batch(self, evolutions: List[ConceptEvolution]) -> None:
        for e in evolutions:
            self.save(e)

    def list_by_to_version(self, to_concept_version_id: uuid.UUID) -> List[ConceptEvolution]:
        stmt = select(ConceptEvolutionModel).where(ConceptEvolutionModel.to_concept_version_id == to_concept_version_id)
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_evolution_entity(m) for m in models]

    def list_by_concept_timeline(self, concept_id: uuid.UUID) -> List[ConceptEvolution]:
        stmt = (
            select(ConceptEvolutionModel)
            .join(ConceptVersionModel, ConceptEvolutionModel.to_concept_version_id == ConceptVersionModel.id)
            .where(ConceptVersionModel.concept_id == concept_id)
            .order_by(ConceptVersionModel.version_number.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_evolution_entity(m) for m in models]


class SAConceptDriftRepository(IConceptDriftRepository):
    """SQLAlchemy repository for ConceptDrift entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, drift: ConceptDrift) -> None:
        model = ConceptMapper.to_concept_drift_model(drift)
        self.session.merge(model)

    def get_by_concept_and_commits(self, concept_id: uuid.UUID, baseline_commit: str, current_commit: str) -> Optional[ConceptDrift]:
        stmt = select(ConceptDriftModel).where(
            and_(
                ConceptDriftModel.concept_id == concept_id,
                ConceptDriftModel.baseline_commit == baseline_commit,
                ConceptDriftModel.current_commit == current_commit,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return ConceptMapper.to_concept_drift_entity(model) if model else None

    def list_by_concept(self, concept_id: uuid.UUID) -> List[ConceptDrift]:
        stmt = select(ConceptDriftModel).where(ConceptDriftModel.concept_id == concept_id)
        models = self.session.execute(stmt).scalars().all()
        return [ConceptMapper.to_concept_drift_entity(m) for m in models]

