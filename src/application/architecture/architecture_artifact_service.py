"""Architecture Artifact Service for the Architectural Intelligence Layer."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from src.application.ports.unit_of_work import IUnitOfWork
from src.infrastructure.persistence.models.knowledge_artifact_model import KnowledgeArtifactModel

class ArchitectureArtifactService:
    """Service to convert architecture engine outputs to KnowledgeArtifacts and persist them."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def persist_artifact(self, repository_id: uuid.UUID, artifact_type: str, source: str, confidence: float, commit_hash: str, provenance: Dict[str, Any]) -> None:
        """Persists a single KnowledgeArtifact."""
        with self.uow:
            artifact = KnowledgeArtifactModel(
                id=uuid.uuid4(),
                repository_id=repository_id,
                artifact_type=artifact_type,
                source=source,
                confidence=confidence,
                valid_from_commit=commit_hash,
                valid_to_commit=None,
                observed_at=datetime.utcnow(),
                artifact_version=1,
                provenance=provenance
            )
            self.uow.knowledge_artifacts.add(artifact)
            self.uow.commit()

    def persist_profile(self, repository_id: uuid.UUID, commit_hash: str, profile_data: Dict[str, Any]) -> None:
        from src.infrastructure.persistence.models.architecture_models import ArchitectureProfileModel
        with self.uow:
            model = ArchitectureProfileModel(
                id=uuid.uuid4(),
                repository_id=str(repository_id),
                commit_hash=commit_hash,
                architecture_type=profile_data.get("architecture_type", "UNKNOWN"),
                description=profile_data.get("description", ""),
                confidence=profile_data.get("confidence", {}),
                evidence=profile_data.get("evidence", {}),
                detected_at=datetime.utcnow()
            )
            self.uow.architecture_profiles.add(model)
            
            # Also persist as a generic knowledge artifact
            artifact = KnowledgeArtifactModel(
                id=uuid.uuid4(),
                repository_id=repository_id,
                artifact_type="architecture_profile",
                source="ArchitectureReasoningEngine",
                confidence=profile_data.get("confidence", {}).get("score", 0.0),
                valid_from_commit=commit_hash,
                observed_at=datetime.utcnow(),
                artifact_version=1,
                provenance={"profile_id": str(model.id)}
            )
            self.uow.knowledge_artifacts.add(artifact)
            self.uow.commit()
            
    def persist_fitness(self, repository_id: uuid.UUID, commit_hash: str, fitness_data: Dict[str, Any]) -> None:
        from src.infrastructure.persistence.models.architecture_models import ArchitectureFitnessModel
        with self.uow:
            model = ArchitectureFitnessModel(
                id=uuid.uuid4(),
                repository_id=str(repository_id),
                commit_hash=commit_hash,
                coupling_score=fitness_data.get("coupling_score", 0.0),
                cohesion_score=fitness_data.get("cohesion_score", 0.0),
                instability_score=fitness_data.get("instability_score", 0.0),
                abstractness_score=fitness_data.get("abstractness_score", 0.0),
                distance_from_main_sequence=fitness_data.get("distance_from_main_sequence", 0.0),
                cyclicity_score=fitness_data.get("cyclicity_score", 0.0),
                layer_violation_score=fitness_data.get("layer_violation_score", 0.0),
                overall_score=fitness_data.get("overall_score", 0.0),
                formulas=fitness_data.get("formulas", {}),
                computed_at=datetime.utcnow()
            )
            self.uow.architecture_fitness.add(model)
            
            artifact = KnowledgeArtifactModel(
                id=uuid.uuid4(),
                repository_id=repository_id,
                artifact_type="architecture_fitness",
                source="FitnessFunctionEngine",
                confidence=1.0,
                valid_from_commit=commit_hash,
                observed_at=datetime.utcnow(),
                artifact_version=1,
                provenance={"fitness_id": str(model.id)}
            )
            self.uow.knowledge_artifacts.add(artifact)
            self.uow.commit()

    def persist_violations(self, repository_id: uuid.UUID, commit_hash: str, violations: List[Dict[str, Any]]) -> None:
        from src.infrastructure.persistence.models.architecture_models import ArchitectureViolationModel
        with self.uow:
            for violation in violations:
                model = ArchitectureViolationModel(
                    id=uuid.uuid4(),
                    repository_id=str(repository_id),
                    commit_hash=commit_hash,
                    rule_name=violation.get("rule_name", ""),
                    severity=violation.get("severity", "INFO"),
                    affected_entities=violation.get("affected_entities", []),
                    affected_capabilities=violation.get("affected_capabilities", []),
                    reason=violation.get("reason", ""),
                    evidence=violation.get("evidence", {}),
                    detected_at=datetime.utcnow()
                )
                self.uow.architecture_violations.add(model)
                
                artifact = KnowledgeArtifactModel(
                    id=uuid.uuid4(),
                    repository_id=repository_id,
                    artifact_type="architecture_violation",
                    source="InvariantReasoningEngine",
                    confidence=1.0,
                    valid_from_commit=commit_hash,
                    observed_at=datetime.utcnow(),
                    artifact_version=1,
                    provenance={"violation_id": str(model.id)}
                )
                self.uow.knowledge_artifacts.add(artifact)
            self.uow.commit()

    def persist_snapshot(self, repository_id: uuid.UUID, commit_hash: str, snapshot_data: Dict[str, Any]) -> None:
        from src.infrastructure.persistence.models.architecture_models import ArchitectureSnapshotModel
        with self.uow:
            model = ArchitectureSnapshotModel(
                id=uuid.uuid4(),
                repository_id=str(repository_id),
                commit_hash=commit_hash,
                architecture_profiles=snapshot_data.get("architecture_profiles", []),
                fitness_metrics=snapshot_data.get("fitness_metrics", {}),
                violations=snapshot_data.get("violations", []),
                ownership_profile=snapshot_data.get("ownership_profile", {}),
                generated_at=datetime.utcnow()
            )
            self.uow.architecture_snapshots.add(model)
            
            artifact = KnowledgeArtifactModel(
                id=uuid.uuid4(),
                repository_id=repository_id,
                artifact_type="architecture_snapshot",
                source="ArchitectureSnapshotEngine",
                confidence=1.0,
                valid_from_commit=commit_hash,
                observed_at=datetime.utcnow(),
                artifact_version=1,
                provenance={"snapshot_id": str(model.id)}
            )
            self.uow.knowledge_artifacts.add(artifact)
            self.uow.commit()
