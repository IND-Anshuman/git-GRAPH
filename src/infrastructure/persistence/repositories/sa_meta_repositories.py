"""SQLAlchemy implementations of Phase 5A repositories for meta-ontology and embedding registries."""

from typing import List, Optional
import uuid

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.domain.entities.meta_ontology import MetaType, MetaDefinition, EmbeddingModel, EmbeddingVersion
from src.domain.repositories.meta_ontology_repo import (
    IMetaTypeRepository,
    IMetaDefinitionRepository,
    IEmbeddingModelRepository,
    IEmbeddingVersionRepository,
)
from src.infrastructure.persistence.models.meta_models import (
    MetaTypeModel,
    MetaDefinitionModel,
    EmbeddingModelModel,
    EmbeddingVersionModel,
)


class SAMetaTypeRepository(IMetaTypeRepository):
    """SQLAlchemy repository for MetaType entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, meta_type: MetaType) -> None:
        model = MetaTypeModel(
            id=meta_type.id,
            name=meta_type.name,
            category=meta_type.category,
            status=meta_type.status,
            created_at=meta_type.created_at,
        )
        self.session.merge(model)

    def get_by_id(self, id: str) -> Optional[MetaType]:
        model = self.session.get(MetaTypeModel, id)
        if not model:
            return None
        return MetaType(
            id=model.id,
            name=model.name,
            category=model.category,
            status=model.status,
            created_at=model.created_at,
        )

    def list_all(self) -> List[MetaType]:
        stmt = select(MetaTypeModel)
        models = self.session.execute(stmt).scalars().all()
        return [
            MetaType(
                id=m.id,
                name=m.name,
                category=m.category,
                status=m.status,
                created_at=m.created_at,
            )
            for m in models
        ]

    def list_by_category(self, category: str) -> List[MetaType]:
        stmt = select(MetaTypeModel).where(MetaTypeModel.category == category)
        models = self.session.execute(stmt).scalars().all()
        return [
            MetaType(
                id=m.id,
                name=m.name,
                category=m.category,
                status=m.status,
                created_at=m.created_at,
            )
            for m in models
        ]


class SAMetaDefinitionRepository(IMetaDefinitionRepository):
    """SQLAlchemy repository for MetaDefinition entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, meta_definition: MetaDefinition) -> None:
        model = MetaDefinitionModel(
            id=meta_definition.id,
            type_id=meta_definition.type_id,
            major_version=meta_definition.major_version,
            minor_version=meta_definition.minor_version,
            patch_version=meta_definition.patch_version,
            schema_definition=meta_definition.schema_definition,
            semantic_signature=meta_definition.semantic_signature,
            created_at=meta_definition.created_at,
        )
        self.session.merge(model)

    def get_by_version(self, type_id: str, major: int, minor: int, patch: int) -> Optional[MetaDefinition]:
        stmt = select(MetaDefinitionModel).where(
            and_(
                MetaDefinitionModel.type_id == type_id,
                MetaDefinitionModel.major_version == major,
                MetaDefinitionModel.minor_version == minor,
                MetaDefinitionModel.patch_version == patch,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return MetaDefinition(
            id=model.id,
            type_id=model.type_id,
            major_version=model.major_version,
            minor_version=model.minor_version,
            patch_version=model.patch_version,
            schema_definition=model.schema_definition,
            semantic_signature=model.semantic_signature,
            created_at=model.created_at,
        )

    def get_latest_definition(self, type_id: str) -> Optional[MetaDefinition]:
        stmt = (
            select(MetaDefinitionModel)
            .where(MetaDefinitionModel.type_id == type_id)
            .order_by(
                MetaDefinitionModel.major_version.desc(),
                MetaDefinitionModel.minor_version.desc(),
                MetaDefinitionModel.patch_version.desc(),
            )
            .limit(1)
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return MetaDefinition(
            id=model.id,
            type_id=model.type_id,
            major_version=model.major_version,
            minor_version=model.minor_version,
            patch_version=model.patch_version,
            schema_definition=model.schema_definition,
            semantic_signature=model.semantic_signature,
            created_at=model.created_at,
        )


class SAEmbeddingModelRepository(IEmbeddingModelRepository):
    """SQLAlchemy repository for EmbeddingModel entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, model: EmbeddingModel) -> None:
        db_model = EmbeddingModelModel(
            id=model.id,
            model_name=model.model_name,
            provider=model.provider,
            dimensions=model.dimensions,
            distance_metric=model.distance_metric,
            is_active=model.is_active,
            created_at=model.created_at,
        )
        self.session.merge(db_model)

    def get_by_id(self, id: str) -> Optional[EmbeddingModel]:
        model = self.session.get(EmbeddingModelModel, id)
        if not model:
            return None
        return EmbeddingModel(
            id=model.id,
            model_name=model.model_name,
            provider=model.provider,
            dimensions=model.dimensions,
            distance_metric=model.distance_metric,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    def get_active_model(self) -> Optional[EmbeddingModel]:
        stmt = select(EmbeddingModelModel).where(EmbeddingModelModel.is_active == True).limit(1)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return EmbeddingModel(
            id=model.id,
            model_name=model.model_name,
            provider=model.provider,
            dimensions=model.dimensions,
            distance_metric=model.distance_metric,
            is_active=model.is_active,
            created_at=model.created_at,
        )


class SAEmbeddingVersionRepository(IEmbeddingVersionRepository):
    """SQLAlchemy repository for EmbeddingVersion entities."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, version: EmbeddingVersion) -> None:
        db_model = EmbeddingVersionModel(
            id=version.id,
            model_id=version.model_id,
            version_string=version.version_string,
            configuration=version.configuration,
            registered_at=version.registered_at,
        )
        self.session.merge(db_model)

    def get_by_version(self, model_id: str, version_string: str) -> Optional[EmbeddingVersion]:
        stmt = select(EmbeddingVersionModel).where(
            and_(
                EmbeddingVersionModel.model_id == model_id,
                EmbeddingVersionModel.version_string == version_string,
            )
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return EmbeddingVersion(
            id=model.id,
            model_id=model.model_id,
            version_string=model.version_string,
            configuration=model.configuration,
            registered_at=model.registered_at,
        )
