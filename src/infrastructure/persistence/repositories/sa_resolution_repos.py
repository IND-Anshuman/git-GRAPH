"""SQLAlchemy repositories for the semantic resolution and governance models."""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.persistence.models.resolution_models import (
    SymbolGraphModel,
    SymbolReferenceModel,
    VariableFlowModel,
    CrossFileResolutionModel,
    ExternalDependencyModel,
    AIEvidenceModel,
    RepositoryArchitectureGraphModel,
    ArchitectureRelationshipModel,
    RepositoryStructureGraphModel,
    CompilerOutputVersionModel,
    ReasoningArtifactModel,
    KnowledgeDriftModel,
    ExternalKnowledgeReferenceModel,
)


class SASymbolGraphRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: SymbolGraphModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[SymbolGraphModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[SymbolGraphModel]:
        stmt = select(SymbolGraphModel).where(SymbolGraphModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SASymbolReferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: SymbolReferenceModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[SymbolReferenceModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[SymbolReferenceModel]:
        stmt = select(SymbolReferenceModel).where(SymbolReferenceModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAVariableFlowRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: VariableFlowModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[VariableFlowModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[VariableFlowModel]:
        stmt = select(VariableFlowModel).where(VariableFlowModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACrossFileResolutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CrossFileResolutionModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[CrossFileResolutionModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CrossFileResolutionModel]:
        stmt = select(CrossFileResolutionModel).where(CrossFileResolutionModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAExternalDependencyRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: ExternalDependencyModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[ExternalDependencyModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[ExternalDependencyModel]:
        stmt = select(ExternalDependencyModel).where(ExternalDependencyModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAAIEvidenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: AIEvidenceModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[AIEvidenceModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[AIEvidenceModel]:
        stmt = select(AIEvidenceModel).where(AIEvidenceModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SARepositoryArchitectureGraphRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: RepositoryArchitectureGraphModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[RepositoryArchitectureGraphModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[RepositoryArchitectureGraphModel]:
        stmt = select(RepositoryArchitectureGraphModel).where(RepositoryArchitectureGraphModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAArchitectureRelationshipRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: ArchitectureRelationshipModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[ArchitectureRelationshipModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[ArchitectureRelationshipModel]:
        stmt = select(ArchitectureRelationshipModel).where(ArchitectureRelationshipModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SARepositoryStructureGraphRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: RepositoryStructureGraphModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[RepositoryStructureGraphModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[RepositoryStructureGraphModel]:
        stmt = select(RepositoryStructureGraphModel).where(RepositoryStructureGraphModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACompilerOutputVersionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CompilerOutputVersionModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[CompilerOutputVersionModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CompilerOutputVersionModel]:
        stmt = select(CompilerOutputVersionModel).where(CompilerOutputVersionModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAReasoningArtifactRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: ReasoningArtifactModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[ReasoningArtifactModel]) -> None:
        self.session.add_all(models)

    def get_by_id(self, artifact_id: uuid.UUID) -> Optional[ReasoningArtifactModel]:
        return self.session.get(ReasoningArtifactModel, artifact_id)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[ReasoningArtifactModel]:
        stmt = select(ReasoningArtifactModel).where(ReasoningArtifactModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAKnowledgeDriftRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: KnowledgeDriftModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[KnowledgeDriftModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[KnowledgeDriftModel]:
        stmt = select(KnowledgeDriftModel).where(KnowledgeDriftModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SAExternalKnowledgeReferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: ExternalKnowledgeReferenceModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[ExternalKnowledgeReferenceModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[ExternalKnowledgeReferenceModel]:
        stmt = select(ExternalKnowledgeReferenceModel).where(ExternalKnowledgeReferenceModel.source_repository_id == repository_id)
        return list(self.session.scalars(stmt).all())
