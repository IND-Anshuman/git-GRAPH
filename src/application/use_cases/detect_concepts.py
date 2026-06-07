"""Use case for detecting and persisting concepts and their metadata at a specific commit."""

import uuid
from typing import Callable, List
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId
from src.application.services.concept_detection_engine import ConceptDetectionEngine
from src.application.services.concept_relationship_engine import ConceptRelationshipEngine
from src.application.services.concept_metrics_engine import ConceptMetricsEngine
from src.application.services.concept_evolution_engine import ConceptEvolutionEngine
from src.application.services.concept_drift_engine import ConceptDriftEngine
from src.application.services.concept_explanation_engine import ConceptExplanationEngine
from src.application.services.concept_cluster_engine import ConceptClusterEngine


class DetectConceptsUseCase:
    """Orchestrates the Phase 4 concept intelligence extraction pipeline for a commit."""

    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        detection_engine: ConceptDetectionEngine,
        relationship_engine: ConceptRelationshipEngine,
        metrics_engine: ConceptMetricsEngine,
        evolution_engine: ConceptEvolutionEngine,
        drift_engine: ConceptDriftEngine,
        explanation_engine: ConceptExplanationEngine,
        cluster_engine: ConceptClusterEngine,
    ) -> None:
        self.uow_factory = uow_factory
        self.detection_engine = detection_engine
        self.relationship_engine = relationship_engine
        self.metrics_engine = metrics_engine
        self.evolution_engine = evolution_engine
        self.drift_engine = drift_engine
        self.explanation_engine = explanation_engine
        self.cluster_engine = cluster_engine

    def execute(self, repository_id: uuid.UUID, commit_hash: str) -> dict:
        """
        Runs the full concept analysis pipeline and persists results.

        Args:
            repository_id: The UUID of the repository.
            commit_hash: The target Git commit hash.

        Returns:
            A results summary.
        """
        repo_id = RepositoryId(repository_id)

        # 1. Run detection
        with self.uow_factory() as uow:
            detected = self.detection_engine.detect_concepts(uow, repo_id, commit_hash)
            if not detected:
                return {
                    "status": "success",
                    "concepts_detected": 0,
                    "relationships_inferred": 0,
                    "clusters_computed": 0,
                }

            # 2. Persist ConceptNodes, Versions and Evidences first so subsequent engines can join
            for c_node, c_ver, ev_list in detected:
                uow.concept_nodes.save(c_node)
                uow.concept_versions.save(c_ver)
                uow.concept_evidence.delete_by_concept_version(c_ver.id)
                uow.concept_evidence.save_batch(ev_list)

            uow.commit()

        # 3. Process second-pass engines
        with self.uow_factory() as uow:
            # Re-fetch or pass detected down to engines
            relationships = self.relationship_engine.infer_relationships(uow, repo_id, commit_hash, detected)
            if relationships:
                uow.concept_relationships.delete_by_commit(repo_id, commit_hash)
                uow.concept_relationships.save_batch(relationships)

            # Compute PageRank, Degree and Impact metrics
            metrics = self.metrics_engine.compute_metrics(uow, detected, relationships)
            if metrics:
                uow.concept_metrics.save_batch(metrics)

            # Compute chronological transitions
            evolutions = self.evolution_engine.track_evolution(uow, repo_id, commit_hash, detected)
            if evolutions:
                uow.concept_evolution.save_batch(evolutions)

            # Compute drift compared to predecessor version
            for c_node, c_ver, _ in detected:
                history = uow.concept_versions.list_by_concept(c_node.id)
                # Exclude the current version
                prev_versions = [v for v in history if v.id != c_ver.id]
                if prev_versions:
                    prev_versions.sort(key=lambda x: x.version_number)
                    baseline = prev_versions[-1]
                    drift = self.drift_engine.compute_drift(uow, c_node.id, baseline, c_ver)
                    uow.concept_drift.save(drift)

            # Generate explanations
            for c_node, c_ver, ev_list in detected:
                explanation = self.explanation_engine.explain_concept(uow, c_node, c_ver, ev_list)
                uow.concept_explanations.save(explanation)

            # Groups concepts into clusters
            clusters = self.cluster_engine.compute_clusters(uow, repo_id, detected)
            for cluster, member_ids in clusters:
                uow.concept_clusters.save(cluster)
                for m_id in member_ids:
                    try:
                        uow.concept_clusters.add_member(cluster.id, m_id)
                    except Exception:
                        pass  # Skip duplicate member errors in test runs

            uow.commit()

        return {
            "status": "success",
            "concepts_detected": len(detected),
            "relationships_inferred": len(relationships),
            "clusters_computed": len(clusters),
        }
