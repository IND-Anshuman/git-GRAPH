"""SQLAlchemy implementations of Phase 3 repositories."""

from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.orm import Session

from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.behavior_explanation import BehaviorExplanation
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.logic_cluster import LogicCluster
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.ontology_node import OntologyNode
from src.domain.enums.drift_category import DriftCategory
from src.domain.enums.evidence_type import EvidenceType
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.repositories.behavior_drift_repo import IBehaviorDriftRepository
from src.domain.repositories.behavior_explanation_repo import ILogicExplanationRepository
from src.domain.repositories.behavior_pattern_repo import IBehaviorPatternRepository
from src.domain.repositories.logic_cluster_repo import ILogicClusterRepository
from src.domain.repositories.logic_evidence_repo import ILogicEvidenceRepository
from src.domain.repositories.logic_signature_repo import ILogicSignatureRepository
from src.domain.repositories.logic_transition_repo import ILogicTransitionRepository
from src.domain.repositories.logic_version_repo import ILogicVersionRepository
from src.domain.repositories.ontology_node_repo import IOntologyNodeRepository
from src.infrastructure.persistence.mappers.logic_mapper import LogicMapper
from src.infrastructure.persistence.models.logic_models import (
    BehaviorDriftModel,
    BehaviorExplanationModel,
    BehaviorPatternModel,
    LogicClusterModel,
    LogicClusterMemberModel,
    LogicEvidenceModel,
    LogicSignatureModel,
    LogicTransitionModel,
    LogicVersionModel,
    OntologyNodeModel,
)


# ------------------------------------------------------------------ #
# 1. SALogicSignatureRepository                                      #
# ------------------------------------------------------------------ #
class SALogicSignatureRepository(ILogicSignatureRepository):
    """SQLAlchemy repository for LogicSignature entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, signature: LogicSignature) -> None:
        model = LogicMapper.to_logic_signature_model(signature)
        self.session.merge(model)

    def get_by_id(self, id: uuid.UUID) -> Optional[LogicSignature]:
        model = self.session.get(LogicSignatureModel, id)
        return LogicMapper.to_logic_signature_entity(model) if model else None

    def get_by_canonical_name(
        self, repository_id: RepositoryId, name: str
    ) -> Optional[LogicSignature]:
        stmt = select(LogicSignatureModel).where(
            and_(
                LogicSignatureModel.repository_id == repository_id.value,
                LogicSignatureModel.entity_name == name,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_logic_signature_entity(model) if model else None

    def list_by_repository(self, repository_id: RepositoryId) -> List[LogicSignature]:
        stmt = select(LogicSignatureModel).where(
            LogicSignatureModel.repository_id == repository_id.value
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_signature_entity(m) for m in models]

    def list_by_ontology_node(self, ontology_node_id: str) -> List[LogicSignature]:
        stmt = select(LogicSignatureModel).where(
            LogicSignatureModel.primary_ontology_node_id == ontology_node_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_signature_entity(m) for m in models]

    def delete_by_repository(self, repository_id: RepositoryId) -> None:
        stmt = delete(LogicSignatureModel).where(
            LogicSignatureModel.repository_id == repository_id.value
        )
        self.session.execute(stmt)


# ------------------------------------------------------------------ #
# 2. SALogicVersionRepository                                        #
# ------------------------------------------------------------------ #
class SALogicVersionRepository(ILogicVersionRepository):
    """SQLAlchemy repository for LogicVersion entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, version: LogicVersion) -> None:
        model = LogicMapper.to_logic_version_model(version)
        self.session.merge(model)

    def save_batch(self, versions: List[LogicVersion]) -> None:
        models = [LogicMapper.to_logic_version_model(v) for v in versions]
        self.session.add_all(models)

    def get_by_id(self, id: uuid.UUID) -> Optional[LogicVersion]:
        model = self.session.get(LogicVersionModel, id)
        return LogicMapper.to_logic_version_entity(model) if model else None

    def get_by_entity_at_commit(
        self, seid: SEID, commit_hash: str
    ) -> List[LogicVersion]:
        # Filter logic versions by entity seid (stored in metadata) and commit
        stmt = select(LogicVersionModel).where(
            and_(
                LogicVersionModel.commit_hash == commit_hash,
                LogicVersionModel.metadata_["entity_seid"].as_string() == str(seid.value),
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_version_entity(m) for m in models]

    def get_primary_by_entity_at_commit(
        self, seid: SEID, commit_hash: str
    ) -> Optional[LogicVersion]:
        # Filter primary logic versions
        stmt = select(LogicVersionModel).where(
            and_(
                LogicVersionModel.commit_hash == commit_hash,
                LogicVersionModel.metadata_["entity_seid"].as_string() == str(seid.value),
                LogicVersionModel.metadata_["is_primary"].as_boolean() == True,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_logic_version_entity(model) if model else None

    def list_by_signature(self, logic_signature_id: uuid.UUID) -> List[LogicVersion]:
        stmt = (
            select(LogicVersionModel)
            .where(LogicVersionModel.signature_id == logic_signature_id)
            .order_by(LogicVersionModel.version_number.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_version_entity(m) for m in models]

    def list_by_entity_timeline(self, seid: SEID) -> List[LogicVersion]:
        stmt = (
            select(LogicVersionModel)
            .where(LogicVersionModel.metadata_["entity_seid"].as_string() == str(seid.value))
            .order_by(LogicVersionModel.version_number.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_version_entity(m) for m in models]

    def get_previous_versions(
        self, seid: SEID, commit_hash: str
    ) -> List[LogicVersion]:
        # Find all versions for the entity before this commit
        # Order chronologically by version number
        stmt = (
            select(LogicVersionModel)
            .where(
                and_(
                    LogicVersionModel.metadata_["entity_seid"].as_string() == str(seid.value),
                    LogicVersionModel.commit_hash != commit_hash,
                )
            )
            .order_by(LogicVersionModel.version_number.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_version_entity(m) for m in models]


# ------------------------------------------------------------------ #
# 3. SALogicTransitionRepository                                      #
# ------------------------------------------------------------------ #
class SALogicTransitionRepository(ILogicTransitionRepository):
    """SQLAlchemy repository for LogicTransition entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, transition: LogicTransition) -> None:
        model = LogicMapper.to_logic_transition_model(transition)
        self.session.merge(model)

    def save_batch(self, transitions: List[LogicTransition]) -> None:
        models = [LogicMapper.to_logic_transition_model(t) for t in transitions]
        self.session.add_all(models)

    def get_by_id(self, id: uuid.UUID) -> Optional[LogicTransition]:
        model = self.session.get(LogicTransitionModel, id)
        return LogicMapper.to_logic_transition_entity(model) if model else None

    def get_by_from_version(self, from_version_id: uuid.UUID) -> List[LogicTransition]:
        stmt = select(LogicTransitionModel).where(
            LogicTransitionModel.from_version_id == from_version_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_transition_entity(m) for m in models]

    def get_by_to_version(self, to_version_id: uuid.UUID) -> List[LogicTransition]:
        stmt = select(LogicTransitionModel).where(
            LogicTransitionModel.to_version_id == to_version_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_transition_entity(m) for m in models]

    def list_by_signature(
        self, logic_signature_id: uuid.UUID
    ) -> List[LogicTransition]:
        # Transition must link versions belonging to the target signature
        # We can join on LogicVersionModel
        stmt = (
            select(LogicTransitionModel)
            .join(
                LogicVersionModel,
                LogicTransitionModel.to_version_id == LogicVersionModel.id,
            )
            .where(LogicVersionModel.signature_id == logic_signature_id)
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_transition_entity(m) for m in models]


# ------------------------------------------------------------------ #
# 4. SALogicEvidenceRepository                                       #
# ------------------------------------------------------------------ #
class SALogicEvidenceRepository(ILogicEvidenceRepository):
    """SQLAlchemy repository for LogicEvidence entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_batch(self, evidence: List[LogicEvidence]) -> None:
        models = [LogicMapper.to_logic_evidence_model(e) for e in evidence]
        self.session.add_all(models)

    def get_by_logic_version(self, logic_version_id: uuid.UUID) -> List[LogicEvidence]:
        stmt = select(LogicEvidenceModel).where(
            LogicEvidenceModel.version_id == logic_version_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_evidence_entity(m) for m in models]

    def get_by_evidence_type(
        self, logic_version_id: uuid.UUID, evidence_type: EvidenceType
    ) -> List[LogicEvidence]:
        stmt = select(LogicEvidenceModel).where(
            and_(
                LogicEvidenceModel.version_id == logic_version_id,
                LogicEvidenceModel.evidence_type == evidence_type.value,
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_evidence_entity(m) for m in models]

    def delete_by_logic_version(self, logic_version_id: uuid.UUID) -> None:
        stmt = delete(LogicEvidenceModel).where(
            LogicEvidenceModel.version_id == logic_version_id
        )
        self.session.execute(stmt)


# ------------------------------------------------------------------ #
# 5. SABehaviorExplanationRepository                                 #
# ------------------------------------------------------------------ #
class SABehaviorExplanationRepository(ILogicExplanationRepository):
    """SQLAlchemy repository for BehaviorExplanation entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, explanation: BehaviorExplanation) -> None:
        model = LogicMapper.to_behavior_explanation_model(explanation)
        self.session.merge(model)

    def get_by_logic_version(
        self, logic_version_id: uuid.UUID
    ) -> Optional[BehaviorExplanation]:
        stmt = select(BehaviorExplanationModel).where(
            BehaviorExplanationModel.version_id == logic_version_id
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_behavior_explanation_entity(model) if model else None

    def list_by_behavior_name(self, behavior_name: str) -> List[BehaviorExplanation]:
        stmt = select(BehaviorExplanationModel).where(
            BehaviorExplanationModel.metadata_["behavior_name"].as_string()
            == behavior_name
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_explanation_entity(m) for m in models]

    def list_by_ontology_path(self, ontology_path: str) -> List[BehaviorExplanation]:
        stmt = select(BehaviorExplanationModel).where(
            BehaviorExplanationModel.metadata_["ontology_path"].as_string()
            == ontology_path
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_explanation_entity(m) for m in models]

    def mark_stale_by_pattern(self, pattern_id: str) -> int:
        stmt = (
            update(BehaviorExplanationModel)
            .where(
                BehaviorExplanationModel.metadata_["matched_pattern_ids"].contains(
                    [pattern_id]
                )
            )
            .values(metadata_=func.json_set(BehaviorExplanationModel.metadata_, "$.is_stale", True))
        )
        result = self.session.execute(stmt)
        return result.rowcount


# ------------------------------------------------------------------ #
# 6. SABehaviorDriftRepository                                       #
# ------------------------------------------------------------------ #
class SABehaviorDriftRepository(IBehaviorDriftRepository):
    """SQLAlchemy repository for BehaviorDrift entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, drift: BehaviorDrift) -> None:
        model = LogicMapper.to_behavior_drift_model(drift)
        self.session.merge(model)

    def get_by_transition(
        self, logic_transition_id: uuid.UUID
    ) -> Optional[BehaviorDrift]:
        stmt = select(BehaviorDriftModel).where(
            BehaviorDriftModel.transition_id == logic_transition_id
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_behavior_drift_entity(model) if model else None

    def list_by_security_boundary_crossed(
        self, repository_id: RepositoryId
    ) -> List[BehaviorDrift]:
        stmt = (
            select(BehaviorDriftModel)
            .join(
                LogicTransitionModel,
                BehaviorDriftModel.transition_id == LogicTransitionModel.id,
            )
            .join(
                LogicVersionModel,
                LogicTransitionModel.to_version_id == LogicVersionModel.id,
            )
            .join(
                LogicSignatureModel,
                LogicVersionModel.signature_id == LogicSignatureModel.id,
            )
            .where(
                and_(
                    LogicSignatureModel.repository_id == repository_id.value,
                    BehaviorDriftModel.metadata_["security_boundary_crossed"].as_boolean()
                    == True,
                )
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_drift_entity(m) for m in models]

    def list_by_drift_category(
        self, repository_id: RepositoryId, category: DriftCategory
    ) -> List[BehaviorDrift]:
        stmt = (
            select(BehaviorDriftModel)
            .join(
                LogicTransitionModel,
                BehaviorDriftModel.transition_id == LogicTransitionModel.id,
            )
            .join(
                LogicVersionModel,
                LogicTransitionModel.to_version_id == LogicVersionModel.id,
            )
            .join(
                LogicSignatureModel,
                LogicVersionModel.signature_id == LogicSignatureModel.id,
            )
            .where(
                and_(
                    LogicSignatureModel.repository_id == repository_id.value,
                    BehaviorDriftModel.drift_category == category.value,
                )
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_drift_entity(m) for m in models]

    def get_drift_summary(self, repository_id: RepositoryId) -> Dict[str, Any]:
        # Aggregate counts by drift category
        # Get count of security boundary crossings
        stmt_cats = (
            select(
                BehaviorDriftModel.drift_category,
                func.count(BehaviorDriftModel.id),
            )
            .join(
                LogicTransitionModel,
                BehaviorDriftModel.transition_id == LogicTransitionModel.id,
            )
            .join(
                LogicVersionModel,
                LogicTransitionModel.to_version_id == LogicVersionModel.id,
            )
            .join(
                LogicSignatureModel,
                LogicVersionModel.signature_id == LogicSignatureModel.id,
            )
            .where(LogicSignatureModel.repository_id == repository_id.value)
            .group_by(BehaviorDriftModel.drift_category)
        )
        cat_counts = dict(self.session.execute(stmt_cats).all())

        stmt_sec = (
            select(func.count(BehaviorDriftModel.id))
            .join(
                LogicTransitionModel,
                BehaviorDriftModel.transition_id == LogicTransitionModel.id,
            )
            .join(
                LogicVersionModel,
                LogicTransitionModel.to_version_id == LogicVersionModel.id,
            )
            .join(
                LogicSignatureModel,
                LogicVersionModel.signature_id == LogicSignatureModel.id,
            )
            .where(
                and_(
                    LogicSignatureModel.repository_id == repository_id.value,
                    BehaviorDriftModel.metadata_["security_boundary_crossed"].as_boolean()
                    == True,
                )
            )
        )
        sec_crossings = self.session.execute(stmt_sec).scalar() or 0

        return {
            "categories": cat_counts,
            "security_boundary_crossings": sec_crossings,
        }


# ------------------------------------------------------------------ #
# 7. SABehaviorPatternRepository                                     #
# ------------------------------------------------------------------ #
class SABehaviorPatternRepository(IBehaviorPatternRepository):
    """SQLAlchemy repository for BehaviorPattern entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, pattern: BehaviorPattern) -> None:
        model = LogicMapper.to_behavior_pattern_model(pattern)
        self.session.merge(model)

    def save_batch(self, patterns: List[BehaviorPattern]) -> None:
        models = [LogicMapper.to_behavior_pattern_model(p) for p in patterns]
        self.session.add_all(models)

    def get_by_pattern_id(self, pattern_id: str) -> Optional[BehaviorPattern]:
        stmt = select(BehaviorPatternModel).where(
            BehaviorPatternModel.pattern_id == pattern_id
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_behavior_pattern_entity(model) if model else None

    def list_active(self) -> List[BehaviorPattern]:
        stmt = select(BehaviorPatternModel).where(
            BehaviorPatternModel.is_active == True
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_pattern_entity(m) for m in models]

    def list_by_ontology_node(self, ontology_node_id: str) -> List[BehaviorPattern]:
        stmt = select(BehaviorPatternModel).where(
            BehaviorPatternModel.ontology_node_id == ontology_node_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_behavior_pattern_entity(m) for m in models]

    def delete_all(self) -> None:
        self.session.execute(delete(BehaviorPatternModel))


# ------------------------------------------------------------------ #
# 8. SALogicClusterRepository                                        #
# ------------------------------------------------------------------ #
class SALogicClusterRepository(ILogicClusterRepository):
    """SQLAlchemy repository for LogicCluster entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, cluster: LogicCluster) -> None:
        model = LogicMapper.to_logic_cluster_model(cluster)
        self.session.merge(model)

    def get_by_id(self, id: uuid.UUID) -> Optional[LogicCluster]:
        model = self.session.get(LogicClusterModel, id)
        return LogicMapper.to_logic_cluster_entity(model) if model else None

    def list_all(self) -> List[LogicCluster]:
        stmt = select(LogicClusterModel)
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_logic_cluster_entity(m) for m in models]

    def add_member(self, cluster_id: uuid.UUID, signature_id: uuid.UUID) -> None:
        # Check if member already exists
        stmt = select(LogicClusterMemberModel).where(
            and_(
                LogicClusterMemberModel.cluster_id == cluster_id,
                LogicClusterMemberModel.signature_id == signature_id,
            )
        )
        exists = self.session.execute(stmt).scalar_one_or_none()
        if not exists:
            member = LogicClusterMemberModel(
                id=uuid.uuid4(),
                cluster_id=cluster_id,
                signature_id=signature_id,
                is_centroid=False,
                joined_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )
            self.session.add(member)

            # Update count in cluster
            stmt_update = (
                update(LogicClusterModel)
                .where(LogicClusterModel.id == cluster_id)
                .values(member_count=LogicClusterModel.member_count + 1)
            )
            self.session.execute(stmt_update)

    def remove_member(self, cluster_id: uuid.UUID, signature_id: uuid.UUID) -> None:
        stmt_del = delete(LogicClusterMemberModel).where(
            and_(
                LogicClusterMemberModel.cluster_id == cluster_id,
                LogicClusterMemberModel.signature_id == signature_id,
            )
        )
        result = self.session.execute(stmt_del)
        if result.rowcount > 0:
            # Update count in cluster
            stmt_update = (
                update(LogicClusterModel)
                .where(LogicClusterModel.id == cluster_id)
                .values(member_count=func.max(0, LogicClusterModel.member_count - 1))
            )
            self.session.execute(stmt_update)


# ------------------------------------------------------------------ #
# 9. SAOntologyNodeRepository                                        #
# ------------------------------------------------------------------ #
class SAOntologyNodeRepository(IOntologyNodeRepository):
    """SQLAlchemy repository for OntologyNode entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, node: OntologyNode) -> None:
        model = LogicMapper.to_ontology_node_model(node)
        self.session.merge(model)

    def save_batch(self, nodes: List[OntologyNode]) -> None:
        models = [LogicMapper.to_ontology_node_model(n) for n in nodes]
        self.session.add_all(models)

    def get_by_id(self, node_id: str) -> Optional[OntologyNode]:
        stmt = select(OntologyNodeModel).where(
            OntologyNodeModel.node_id == node_id
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return LogicMapper.to_ontology_node_entity(model) if model else None

    def list_by_domain(self, domain: str) -> List[OntologyNode]:
        stmt = select(OntologyNodeModel).where(OntologyNodeModel.domain == domain)
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_ontology_node_entity(m) for m in models]

    def list_children(self, parent_id: str) -> List[OntologyNode]:
        stmt = select(OntologyNodeModel).where(
            OntologyNodeModel.parent_node_id == parent_id
        )
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_ontology_node_entity(m) for m in models]

    def list_all(self) -> List[OntologyNode]:
        stmt = select(OntologyNodeModel)
        models = self.session.execute(stmt).scalars().all()
        return [LogicMapper.to_ontology_node_entity(m) for m in models]

    def delete_all(self) -> None:
        self.session.execute(delete(OntologyNodeModel))

    def get_current_version(self) -> Optional[str]:
        stmt = select(OntologyNodeModel.ontology_version).limit(1)
        return self.session.execute(stmt).scalar()
