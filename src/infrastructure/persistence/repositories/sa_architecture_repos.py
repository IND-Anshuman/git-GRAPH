"""SQLAlchemy repository implementations for the Architectural Intelligence Layer."""

from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import select, delete, and_
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models.architecture_models import (
    ArchitectureProfileModel,
    ArchitectureSnapshotModel,
    ArchitectureFitnessModel,
    ArchitectureViolationModel,
    ArchitectureInvariantModel,
    ArchitectureDriftModel,
    ArchitectureTimelineModel,
    ArchitectureBenchmarkModel,
    ArchitectureSimilarityModel,
    OwnershipProfileModel,
    RefactoringCandidateModel,
    ArchitectureRecommendationModel,
)


class BaseArchitectureRepository:
    """Base repository for architecture models."""

    def __init__(self, session: Session, model_class: type):
        self._session = session
        self._model_class = model_class

    def get_by_id(self, id: uuid.UUID) -> Optional[Any]:
        return self._session.get(self._model_class, id)

    def add(self, entity: Any) -> None:
        self._session.add(entity)

    def add_all(self, entities: List[Any]) -> None:
        self._session.add_all(entities)

    def delete(self, entity: Any) -> None:
        self._session.delete(entity)

    def find_by_repository(self, repository_id: str) -> List[Any]:
        stmt = select(self._model_class).where(self._model_class.repository_id == repository_id)
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureProfileRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureProfileModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[ArchitectureProfileModel]:
        stmt = select(ArchitectureProfileModel).where(
            and_(
                ArchitectureProfileModel.repository_id == repository_id,
                ArchitectureProfileModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureSnapshotRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureSnapshotModel)
        
    def get_latest_for_commit(self, repository_id: str, commit_hash: str) -> Optional[ArchitectureSnapshotModel]:
        stmt = select(ArchitectureSnapshotModel).where(
            and_(
                ArchitectureSnapshotModel.repository_id == repository_id,
                ArchitectureSnapshotModel.commit_hash == commit_hash
            )
        ).order_by(ArchitectureSnapshotModel.generated_at.desc()).limit(1)
        return self._session.execute(stmt).scalars().first()


class SAArchitectureFitnessRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureFitnessModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[ArchitectureFitnessModel]:
        stmt = select(ArchitectureFitnessModel).where(
            and_(
                ArchitectureFitnessModel.repository_id == repository_id,
                ArchitectureFitnessModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureViolationRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureViolationModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[ArchitectureViolationModel]:
        stmt = select(ArchitectureViolationModel).where(
            and_(
                ArchitectureViolationModel.repository_id == repository_id,
                ArchitectureViolationModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureInvariantRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureInvariantModel)
        
    def get_active_invariants(self, repository_id: Optional[str] = None) -> List[ArchitectureInvariantModel]:
        conditions = [ArchitectureInvariantModel.enabled == True]
        if repository_id:
            conditions.append(ArchitectureInvariantModel.repository_id == repository_id)
        stmt = select(ArchitectureInvariantModel).where(and_(*conditions))
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureDriftRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureDriftModel)
        
    def find_between_commits(self, repository_id: str, from_commit: str, to_commit: str) -> List[ArchitectureDriftModel]:
        stmt = select(ArchitectureDriftModel).where(
            and_(
                ArchitectureDriftModel.repository_id == repository_id,
                ArchitectureDriftModel.from_commit == from_commit,
                ArchitectureDriftModel.to_commit == to_commit
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureTimelineRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureTimelineModel)


class SAArchitectureBenchmarkRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureBenchmarkModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[ArchitectureBenchmarkModel]:
        stmt = select(ArchitectureBenchmarkModel).where(
            and_(
                ArchitectureBenchmarkModel.repository_id == repository_id,
                ArchitectureBenchmarkModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureSimilarityRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureSimilarityModel)
        
    def find_similar_repositories(self, repository_id: str) -> List[ArchitectureSimilarityModel]:
        stmt = select(ArchitectureSimilarityModel).where(
            ArchitectureSimilarityModel.source_repository_id == repository_id
        ).order_by(ArchitectureSimilarityModel.similarity_score.desc())
        return list(self._session.execute(stmt).scalars().all())


class SAOwnershipProfileRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, OwnershipProfileModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[OwnershipProfileModel]:
        stmt = select(OwnershipProfileModel).where(
            and_(
                OwnershipProfileModel.repository_id == repository_id,
                OwnershipProfileModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SARefactoringCandidateRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, RefactoringCandidateModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[RefactoringCandidateModel]:
        stmt = select(RefactoringCandidateModel).where(
            and_(
                RefactoringCandidateModel.repository_id == repository_id,
                RefactoringCandidateModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())


class SAArchitectureRecommendationRepository(BaseArchitectureRepository):
    def __init__(self, session: Session):
        super().__init__(session, ArchitectureRecommendationModel)
        
    def find_by_commit(self, repository_id: str, commit_hash: str) -> List[ArchitectureRecommendationModel]:
        stmt = select(ArchitectureRecommendationModel).where(
            and_(
                ArchitectureRecommendationModel.repository_id == repository_id,
                ArchitectureRecommendationModel.commit_hash == commit_hash
            )
        )
        return list(self._session.execute(stmt).scalars().all())
