"""SQLAlchemy implementation of ISourceFileRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.source_file import SourceFile
from src.domain.repositories.source_file_repo import ISourceFileRepository
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.source_file_model import SourceFileModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper


class SASourceFileRepository(ISourceFileRepository):
    """SQLAlchemy repository for SourceFile entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: FileId) -> Optional[SourceFile]:
        model = self.session.get(SourceFileModel, id.value)
        if model:
            return DomainMapper.to_source_file_entity(model)
        return None
        
    def get_by_path(self, repository_id: RepositoryId, file_path: str) -> Optional[SourceFile]:
        stmt = select(SourceFileModel).where(
            SourceFileModel.repository_id == repository_id.value,
            SourceFileModel.file_path == file_path
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if model:
            return DomainMapper.to_source_file_entity(model)
        return None

    def get_by_repository(self, repo_id: RepositoryId) -> List[SourceFile]:
        stmt = select(SourceFileModel).where(SourceFileModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_source_file_entity(m) for m in models]

    def save(self, file: SourceFile) -> None:
        model = DomainMapper.to_source_file_model(file)
        self.session.merge(model)
        
    def save_batch(self, files: List[SourceFile]) -> None:
        raw_models = [DomainMapper.to_source_file_model(f) for f in files]
        # Deduplicate by source file ID and file path
        by_id = {m.id: m for m in raw_models}
        by_path = {m.file_path: m for m in by_id.values()}
        
        for model in by_path.values():
            self.session.merge(model)

    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        stmt = select(SourceFileModel).where(SourceFileModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        for m in models:
            self.session.delete(m)
