"""SQLAlchemy implementation of ICodeEntityRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.code_entity import CodeEntity
from src.domain.repositories.code_entity_repo import ICodeEntityRepository
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.file_id import FileId
from src.domain.enums.entity_type import EntityType
from src.infrastructure.persistence.models.code_entity_model import CodeEntityModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper


class SACodeEntityRepository(ICodeEntityRepository):
    """SQLAlchemy repository for CodeEntity entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_seid(self, seid: SEID) -> Optional[CodeEntity]:
        model = self.session.get(CodeEntityModel, seid.value)
        if model:
            return DomainMapper.to_code_entity(model)
        return None

    def get_by_seids(self, seids: List[SEID]) -> List[CodeEntity]:
        if not seids:
            return []
        
        chunk_size = 500
        seid_values = [s.value for s in seids]
        results = []
        for i in range(0, len(seid_values), chunk_size):
            chunk = seid_values[i:i + chunk_size]
            stmt = select(CodeEntityModel).where(CodeEntityModel.seid.in_(chunk))
            models = self.session.execute(stmt).scalars().all()
            results.extend([DomainMapper.to_code_entity(m) for m in models])
        return results

    def get_by_repository(self, repo_id: RepositoryId, entity_type: EntityType | None = None) -> List[CodeEntity]:
        if entity_type:
            stmt = select(CodeEntityModel).where(
                CodeEntityModel.repository_id == repo_id.value,
                CodeEntityModel.entity_type == entity_type.value
            )
        else:
            stmt = select(CodeEntityModel).where(CodeEntityModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_code_entity(m) for m in models]
        
    def get_by_file(self, file_id: FileId) -> List[CodeEntity]:
        stmt = select(CodeEntityModel).where(CodeEntityModel.file_id == file_id.value)
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_code_entity(m) for m in models]

    def save(self, entity: CodeEntity) -> None:
        model = DomainMapper.to_code_entity_model(entity)
        self.session.merge(model)

    def save_batch(self, entities: List[CodeEntity]) -> None:
        raw_models = [DomainMapper.to_code_entity_model(e) for e in entities]
        if not raw_models:
            return
        
        # Deduplicate by SEID to prevent multiple insertions of the same entity in the same transaction
        by_seid = {m.seid: m for m in raw_models}
        models = list(by_seid.values())
        memo = {}

        def get_depth(m):
            if m.seid in memo:
                return memo[m.seid]
            if not m.parent_seid or m.parent_seid not in by_seid:
                memo[m.seid] = 0
                return 0
            
            # Guard against circular references
            memo[m.seid] = 999
            parent_m = by_seid[m.parent_seid]
            depth = get_depth(parent_m) + 1
            memo[m.seid] = depth
            return depth

        from collections import defaultdict
        depth_groups = defaultdict(list)
        for m in models:
            d = get_depth(m)
            depth_groups[d].append(m)

        for d in sorted(depth_groups.keys()):
            for model in depth_groups[d]:
                self.session.merge(model)
            # Flush this level to the database before processing children
            self.session.flush()

    def delete_by_repository(self, repo_id: RepositoryId) -> None:
        stmt = select(CodeEntityModel).where(CodeEntityModel.repository_id == repo_id.value)
        models = self.session.execute(stmt).scalars().all()
        for m in models:
            self.session.delete(m)
