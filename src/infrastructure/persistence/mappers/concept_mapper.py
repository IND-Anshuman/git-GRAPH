"""Mapper translating between Concept Graph domain entities and database models."""

import uuid
from typing import Any, Dict

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_cluster import ConceptCluster
from src.domain.entities.concept_explanation import ConceptExplanation
from src.domain.entities.concept_evolution import ConceptEvolution
from src.domain.entities.concept_metrics import ConceptMetrics
from src.domain.entities.concept_drift import ConceptDrift
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.enums.concept_transition_type import ConceptTransitionType
from src.domain.value_objects.repository_id import RepositoryId

from src.infrastructure.persistence.models.concept_models import (
    ConceptNodeModel,
    ConceptVersionModel,
    ConceptEvidenceModel,
    ConceptRelationshipModel,
    ConceptClusterModel,
    ConceptExplanationModel,
    ConceptMetricsModel,
    ConceptEvolutionModel,
    ConceptDriftModel,
)


class ConceptMapper:
    """Utility class providing static conversion methods for concept data classes."""

    # 1. ConceptNode
    @staticmethod
    def to_concept_node_model(entity: ConceptNode) -> ConceptNodeModel:
        return ConceptNodeModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            ontology_node_id=entity.ontology_node_id,
            name=entity.name,
            description=entity.description,
            is_system_defined=entity.is_system_defined,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_concept_node_entity(model: ConceptNodeModel) -> ConceptNode:
        return ConceptNode(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            ontology_node_id=model.ontology_node_id,
            name=model.name,
            description=model.description,
            is_system_defined=model.is_system_defined,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # 2. ConceptVersion
    @staticmethod
    def to_concept_version_model(entity: ConceptVersion) -> ConceptVersionModel:
        return ConceptVersionModel(
            id=entity.id,
            concept_id=entity.concept_id,
            commit_hash=entity.commit_hash,
            version_number=entity.version_number,
            confidence=entity.confidence,
            is_active=entity.is_active,
            metadata_=entity.metadata,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_concept_version_entity(model: ConceptVersionModel) -> ConceptVersion:
        return ConceptVersion(
            id=model.id,
            concept_id=model.concept_id,
            commit_hash=model.commit_hash,
            version_number=model.version_number,
            confidence=float(model.confidence),
            is_active=model.is_active,
            metadata=model.metadata_,
            created_at=model.created_at,
        )

    # 3. ConceptEvidence
    @staticmethod
    def to_concept_evidence_model(entity: ConceptEvidence) -> ConceptEvidenceModel:
        return ConceptEvidenceModel(
            id=entity.id,
            concept_version_id=entity.concept_version_id,
            evidence_type=entity.evidence_type,
            target_id=entity.target_id,
            confidence_contribution=entity.confidence_contribution,
            metadata_=entity.metadata,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_concept_evidence_entity(model: ConceptEvidenceModel) -> ConceptEvidence:
        return ConceptEvidence(
            id=model.id,
            concept_version_id=model.concept_version_id,
            evidence_type=model.evidence_type,
            target_id=model.target_id,
            confidence_contribution=float(model.confidence_contribution),
            metadata=model.metadata_,
            created_at=model.created_at,
        )

    # 4. ConceptRelationship
    @staticmethod
    def to_concept_relationship_model(entity: ConceptRelationship) -> ConceptRelationshipModel:
        return ConceptRelationshipModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            commit_hash=entity.commit_hash,
            from_concept_id=entity.from_concept_id,
            to_concept_id=entity.to_concept_id,
            relationship_type=entity.relationship_type,
            confidence=entity.confidence,
            metadata_=entity.metadata,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_concept_relationship_entity(model: ConceptRelationshipModel) -> ConceptRelationship:
        return ConceptRelationship(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            commit_hash=model.commit_hash,
            from_concept_id=model.from_concept_id,
            to_concept_id=model.to_concept_id,
            relationship_type=model.relationship_type,
            confidence=float(model.confidence),
            metadata=model.metadata_,
            created_at=model.created_at,
        )

    # 5. ConceptCluster
    @staticmethod
    def to_concept_cluster_model(entity: ConceptCluster) -> ConceptClusterModel:
        return ConceptClusterModel(
            id=entity.id,
            cluster_key=entity.cluster_key,
            cluster_label=entity.cluster_label,
            cohesion_score=entity.cohesion_score,
            member_count=entity.member_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_concept_cluster_entity(model: ConceptClusterModel) -> ConceptCluster:
        return ConceptCluster(
            id=model.id,
            cluster_key=model.cluster_key,
            cluster_label=model.cluster_label,
            cohesion_score=float(model.cohesion_score),
            member_count=model.member_count,
            metadata=model.metadata_ if hasattr(model, "metadata_") else {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # 6. ConceptExplanation
    @staticmethod
    def to_concept_explanation_model(entity: ConceptExplanation) -> ConceptExplanationModel:
        return ConceptExplanationModel(
            id=entity.id,
            concept_version_id=entity.concept_version_id,
            summary=entity.summary,
            detail=entity.detail,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_concept_explanation_entity(model: ConceptExplanationModel) -> ConceptExplanation:
        return ConceptExplanation(
            id=model.id,
            concept_version_id=model.concept_version_id,
            summary=model.summary,
            detail=model.detail,
            created_at=model.created_at,
        )

    # 7. ConceptEvolution
    @staticmethod
    def to_concept_evolution_model(entity: ConceptEvolution) -> ConceptEvolutionModel:
        return ConceptEvolutionModel(
            id=entity.id,
            from_concept_version_id=entity.from_concept_version_id,
            to_concept_version_id=entity.to_concept_version_id,
            transition_type=entity.transition_type,
            similarity_score=entity.similarity_score,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_concept_evolution_entity(model: ConceptEvolutionModel) -> ConceptEvolution:
        return ConceptEvolution(
            id=model.id,
            from_concept_version_id=model.from_concept_version_id,
            to_concept_version_id=model.to_concept_version_id,
            transition_type=model.transition_type,
            similarity_score=float(model.similarity_score),
            created_at=model.created_at,
        )

    # 8. ConceptMetrics
    @staticmethod
    def to_concept_metrics_model(entity: ConceptMetrics) -> ConceptMetricsModel:
        return ConceptMetricsModel(
            id=entity.id,
            concept_version_id=entity.concept_version_id,
            entity_count=entity.entity_count,
            file_count=entity.file_count,
            in_degree=entity.in_degree,
            out_degree=entity.out_degree,
            degree_centrality=entity.degree_centrality,
            betweenness_centrality=entity.betweenness_centrality,
            pagerank_score=entity.pagerank_score,
            impact_score=entity.impact_score,
            computed_at=entity.computed_at,
        )

    @staticmethod
    def to_concept_metrics_entity(model: ConceptMetricsModel) -> ConceptMetrics:
        return ConceptMetrics(
            id=model.id,
            concept_version_id=model.concept_version_id,
            entity_count=model.entity_count,
            file_count=model.file_count,
            in_degree=model.in_degree,
            out_degree=model.out_degree,
            degree_centrality=float(model.degree_centrality),
            betweenness_centrality=float(model.betweenness_centrality),
            pagerank_score=float(model.pagerank_score),
            impact_score=float(model.impact_score),
            computed_at=model.computed_at,
        )

    # 9. ConceptDrift
    @staticmethod
    def to_concept_drift_model(entity: ConceptDrift) -> ConceptDriftModel:
        return ConceptDriftModel(
            id=entity.id,
            concept_id=entity.concept_id,
            baseline_commit=entity.baseline_commit,
            current_commit=entity.current_commit,
            drift_score=entity.drift_score,
            drift_category=entity.drift_category,
            dimension_scores=entity.dimension_scores,
            computed_at=entity.computed_at,
        )

    @staticmethod
    def to_concept_drift_entity(model: ConceptDriftModel) -> ConceptDrift:
        return ConceptDrift(
            id=model.id,
            concept_id=model.concept_id,
            baseline_commit=model.baseline_commit,
            current_commit=model.current_commit,
            drift_score=float(model.drift_score),
            drift_category=model.drift_category,
            dimension_scores=model.dimension_scores,
            computed_at=model.computed_at,
        )

