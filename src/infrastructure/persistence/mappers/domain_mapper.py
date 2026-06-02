"""Domain to Model mapper."""

from typing import Optional

from src.domain.entities.repository import RepositoryEntity
from src.domain.entities.source_file import SourceFile
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.relationship import Relationship
from src.domain.entities.commit import Commit
from src.domain.entities.entity_version import EntityVersion
from src.domain.entities.relationship_version import RelationshipVersion
from src.domain.entities.change_event import ChangeEvent
from src.domain.entities.repository_snapshot import RepositorySnapshot
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.code_location import CodeLocation
from src.domain.value_objects.fingerprint import StructuralFingerprint
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.enums.mutation_type import MutationType

from src.infrastructure.persistence.models.repository_model import RepositoryModel
from src.infrastructure.persistence.models.source_file_model import SourceFileModel
from src.infrastructure.persistence.models.code_entity_model import CodeEntityModel
from src.infrastructure.persistence.models.relationship_model import RelationshipModel
from src.infrastructure.persistence.models.commit_model import CommitModel
from src.infrastructure.persistence.models.entity_version_model import EntityVersionModel
from src.infrastructure.persistence.models.relationship_version_model import RelationshipVersionModel
from src.infrastructure.persistence.models.change_event_model import ChangeEventModel
from src.infrastructure.persistence.models.snapshot_model import RepositorySnapshotModel


class DomainMapper:
    """Mapper between domain entities and database models."""

    @staticmethod
    def _parse_enum(enum_cls, val):
        if val is None:
            return None
        if isinstance(val, enum_cls):
            return val
        if isinstance(val, int):
            try:
                return enum_cls(val)
            except ValueError:
                pass
        if isinstance(val, str):
            try:
                return enum_cls(int(val))
            except ValueError:
                pass
            try:
                return enum_cls[val]
            except KeyError:
                pass
        return enum_cls(val)

    @staticmethod
    def to_repository_model(entity: RepositoryEntity) -> RepositoryModel:
        return RepositoryModel(
            id=entity.id.value,
            name=entity.name,
            url=entity.url,
            default_branch=entity.default_branch,
            local_path=entity.local_path,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_repository_entity(model: RepositoryModel) -> RepositoryEntity:
        return RepositoryEntity(
            id=RepositoryId(model.id),
            name=model.name,
            url=model.url,
            default_branch=model.default_branch,
            local_path=model.local_path,
            status=DomainMapper._parse_enum(AnalysisStatus, model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata=model.metadata_
        )

    @staticmethod
    def to_source_file_model(entity: SourceFile) -> SourceFileModel:
        return SourceFileModel(
            id=entity.id.value,
            repository_id=entity.repository_id.value,
            file_path=entity.file_path,
            language=entity.language.value,
            content_hash=entity.content_hash,
            line_count=entity.line_count,
            size_bytes=entity.size_bytes
        )

    @staticmethod
    def to_source_file_entity(model: SourceFileModel) -> SourceFile:
        return SourceFile(
            id=FileId(model.id),
            repository_id=RepositoryId(model.repository_id),
            file_path=model.file_path,
            language=DomainMapper._parse_enum(SupportedLanguage, model.language),
            content_hash=model.content_hash,
            line_count=model.line_count,
            size_bytes=model.size_bytes
        )

    @staticmethod
    def to_code_entity_model(entity: CodeEntity) -> CodeEntityModel:
        return CodeEntityModel(
            seid=entity.seid.value,
            entity_type=entity.entity_type.value,
            name=entity.name,
            qualified_name=entity.qualified_name,
            file_id=entity.file_id.value,
            repository_id=entity.repository_id.value,
            parent_seid=entity.parent_seid.value if entity.parent_seid else None,
            language=entity.language.value,
            file_path=entity.location.file_path,
            start_line=entity.location.start_line,
            end_line=entity.location.end_line,
            start_column=entity.location.start_column,
            end_column=entity.location.end_column,
            content_hash=entity.content_hash,
            structural_fingerprint=entity.structural_fingerprint.value if entity.structural_fingerprint else None,
            source_text=entity.source_text,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_code_entity(model: CodeEntityModel) -> CodeEntity:
        return CodeEntity(
            seid=SEID(model.seid),
            entity_type=DomainMapper._parse_enum(EntityType, model.entity_type),
            name=model.name,
            qualified_name=model.qualified_name,
            file_id=FileId(model.file_id),
            repository_id=RepositoryId(model.repository_id),
            parent_seid=SEID(model.parent_seid) if model.parent_seid else None,
            language=DomainMapper._parse_enum(SupportedLanguage, model.language),
            location=CodeLocation(
                file_path=model.file_path,
                start_line=model.start_line,
                end_line=model.end_line,
                start_column=model.start_column,
                end_column=model.end_column
            ),
            content_hash=model.content_hash,
            structural_fingerprint=StructuralFingerprint(model.structural_fingerprint) if model.structural_fingerprint else None,
            source_text=model.source_text,
            metadata=model.metadata_
        )

    @staticmethod
    def to_relationship_model(entity: Relationship) -> RelationshipModel:
        return RelationshipModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            relationship_type=entity.relationship_type.value,
            source_seid=entity.source_seid.value,
            target_seid=entity.target_seid.value,
            confidence=entity.confidence,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_relationship_entity(model: RelationshipModel) -> Relationship:
        return Relationship(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            relationship_type=DomainMapper._parse_enum(RelationshipType, model.relationship_type),
            source_seid=SEID(model.source_seid),
            target_seid=SEID(model.target_seid),
            confidence=model.confidence,
            metadata=model.metadata_
        )

    @staticmethod
    def to_commit_model(entity: Commit) -> CommitModel:
        return CommitModel(
            hash=entity.hash,
            repository_id=entity.repository_id.value,
            author=entity.author,
            email=entity.email,
            timestamp=entity.timestamp,
            message=entity.message,
            parent_hashes=entity.parent_hashes
        )

    @staticmethod
    def to_commit_entity(model: CommitModel) -> Commit:
        return Commit(
            hash=model.hash,
            repository_id=RepositoryId(model.repository_id),
            author=model.author,
            email=model.email,
            timestamp=model.timestamp,
            message=model.message,
            parent_hashes=model.parent_hashes
        )

    @staticmethod
    def to_entity_version_model(entity: EntityVersion) -> EntityVersionModel:
        return EntityVersionModel(
            id=entity.id,
            seid=entity.seid.value,
            commit_hash=entity.commit_hash,
            version_ordinal=entity.version_ordinal,
            mutation_type=entity.mutation_type.value,
            canonical_name=entity.canonical_name,
            file_path=entity.file_path,
            start_line=entity.start_line,
            end_line=entity.end_line,
            content_hash=entity.content_hash,
            structural_fingerprint=entity.structural_fingerprint,
            source_text=entity.source_text,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_entity_version_entity(model: EntityVersionModel) -> EntityVersion:
        return EntityVersion(
            id=model.id,
            seid=SEID(model.seid),
            commit_hash=model.commit_hash,
            version_ordinal=model.version_ordinal,
            mutation_type=DomainMapper._parse_enum(MutationType, model.mutation_type),
            canonical_name=model.canonical_name,
            file_path=model.file_path,
            start_line=model.start_line,
            end_line=model.end_line,
            content_hash=model.content_hash,
            structural_fingerprint=model.structural_fingerprint,
            source_text=model.source_text,
            metadata=model.metadata_
        )

    @staticmethod
    def to_relationship_version_model(entity: RelationshipVersion) -> RelationshipVersionModel:
        return RelationshipVersionModel(
            id=entity.id,
            relationship_id=entity.relationship_id,
            commit_hash=entity.commit_hash,
            mutation_type=entity.mutation_type.value,
            version_ordinal=entity.version_ordinal,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_relationship_version_entity(model: RelationshipVersionModel) -> RelationshipVersion:
        return RelationshipVersion(
            id=model.id,
            relationship_id=model.relationship_id,
            commit_hash=model.commit_hash,
            mutation_type=DomainMapper._parse_enum(MutationType, model.mutation_type),
            version_ordinal=model.version_ordinal,
            metadata=model.metadata_
        )

    @staticmethod
    def to_change_event_model(entity: ChangeEvent) -> ChangeEventModel:
        return ChangeEventModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            commit_hash=entity.commit_hash,
            seid=entity.seid.value,
            change_type=entity.change_type.value,
            metadata_=entity.metadata
        )

    @staticmethod
    def to_change_event_entity(model: ChangeEventModel) -> ChangeEvent:
        return ChangeEvent(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            commit_hash=model.commit_hash,
            seid=SEID(model.seid),
            change_type=DomainMapper._parse_enum(MutationType, model.change_type),
            metadata=model.metadata_
        )

    @staticmethod
    def to_snapshot_model(entity: RepositorySnapshot) -> RepositorySnapshotModel:
        return RepositorySnapshotModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            commit_hash=entity.commit_hash,
            entity_seids=[str(seid) for seid in entity.entity_seids],
            snapshot_data=entity.snapshot_data,
            created_at=entity.created_at
        )

    @staticmethod
    def to_snapshot_entity(model: RepositorySnapshotModel) -> RepositorySnapshot:
        return RepositorySnapshot(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            commit_hash=model.commit_hash,
            entity_seids=[SEID.from_string(val) for val in model.entity_seids],
            snapshot_data=model.snapshot_data,
            created_at=model.created_at
        )
