"""SQLAlchemy repositories for the Capability Intelligence Layer (CIL) (Phase 6)."""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.persistence.models.capability_models import (
    CapabilityModel,
    CapabilityCandidateModel,
    CapabilityRelationshipModel,
    CapabilityFingerprintModel,
    CapabilityEvolutionModel,
    CapabilityTimelineModel,
    CapabilityDependencyModel,
    CapabilityHealthModel,
    CapabilityBlastRadiusModel,
    CapabilityProvenanceModel,
    CapabilityConfidenceModel,
    CapabilityOverlapModel,
    CapabilityStabilityModel,
    CapabilitySnapshotModel,
    CapabilityBoundaryModel,
    CapabilityCohesionModel,
    CapabilityCouplingModel,
    CapabilityEmbeddingModel,
    CapabilityTaxonomyCandidateModel,
)


class SACapabilityRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[CapabilityModel]) -> None:
        self.session.add_all(models)

    def get_by_id(self, id: uuid.UUID) -> Optional[CapabilityModel]:
        stmt = select(CapabilityModel).where(CapabilityModel.id == id)
        return self.session.scalars(stmt).first()

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityModel]:
        stmt = select(CapabilityModel).where(CapabilityModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityCandidateRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityCandidateModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[CapabilityCandidateModel]) -> None:
        self.session.add_all(models)

    def get_by_id(self, id: uuid.UUID) -> Optional[CapabilityCandidateModel]:
        stmt = select(CapabilityCandidateModel).where(CapabilityCandidateModel.id == id)
        return self.session.scalars(stmt).first()

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityCandidateModel]:
        stmt = select(CapabilityCandidateModel).where(CapabilityCandidateModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityRelationshipRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityRelationshipModel) -> None:
        self.session.add(model)

    def save_batch(self, models: List[CapabilityRelationshipModel]) -> None:
        self.session.add_all(models)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityRelationshipModel]:
        stmt = select(CapabilityRelationshipModel).where(CapabilityRelationshipModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityFingerprintRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityFingerprintModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityFingerprintModel]:
        stmt = select(CapabilityFingerprintModel).where(CapabilityFingerprintModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityEvolutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityEvolutionModel) -> None:
        self.session.add(model)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityEvolutionModel]:
        stmt = select(CapabilityEvolutionModel).where(CapabilityEvolutionModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityTimelineRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityTimelineModel) -> None:
        self.session.add(model)

    def list_by_capability(self, capability_id: uuid.UUID) -> List[CapabilityTimelineModel]:
        stmt = select(CapabilityTimelineModel).where(CapabilityTimelineModel.capability_id == capability_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityDependencyRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityDependencyModel) -> None:
        self.session.add(model)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityDependencyModel]:
        stmt = select(CapabilityDependencyModel).where(CapabilityDependencyModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityHealthRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityHealthModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityHealthModel]:
        stmt = select(CapabilityHealthModel).where(CapabilityHealthModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityBlastRadiusRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityBlastRadiusModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityBlastRadiusModel]:
        stmt = select(CapabilityBlastRadiusModel).where(CapabilityBlastRadiusModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityProvenanceRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityProvenanceModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityProvenanceModel]:
        stmt = select(CapabilityProvenanceModel).where(CapabilityProvenanceModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityConfidenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityConfidenceModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityConfidenceModel]:
        stmt = select(CapabilityConfidenceModel).where(CapabilityConfidenceModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityOverlapRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityOverlapModel) -> None:
        self.session.add(model)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityOverlapModel]:
        stmt = select(CapabilityOverlapModel).where(CapabilityOverlapModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())


class SACapabilityStabilityRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityStabilityModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityStabilityModel]:
        stmt = select(CapabilityStabilityModel).where(CapabilityStabilityModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilitySnapshotRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilitySnapshotModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilitySnapshotModel]:
        stmt = select(CapabilitySnapshotModel).where(CapabilitySnapshotModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityBoundaryRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityBoundaryModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityBoundaryModel]:
        stmt = select(CapabilityBoundaryModel).where(CapabilityBoundaryModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityCohesionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityCohesionModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityCohesionModel]:
        stmt = select(CapabilityCohesionModel).where(CapabilityCohesionModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityCouplingRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityCouplingModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityCouplingModel]:
        stmt = select(CapabilityCouplingModel).where(CapabilityCouplingModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityEmbeddingRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityEmbeddingModel) -> None:
        self.session.add(model)

    def get_by_capability(self, capability_id: uuid.UUID) -> Optional[CapabilityEmbeddingModel]:
        stmt = select(CapabilityEmbeddingModel).where(CapabilityEmbeddingModel.capability_id == capability_id)
        return self.session.scalars(stmt).first()


class SACapabilityTaxonomyCandidateRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, model: CapabilityTaxonomyCandidateModel) -> None:
        self.session.add(model)

    def list_by_repository(self, repository_id: uuid.UUID) -> List[CapabilityTaxonomyCandidateModel]:
        stmt = select(CapabilityTaxonomyCandidateModel).where(CapabilityTaxonomyCandidateModel.repository_id == repository_id)
        return list(self.session.scalars(stmt).all())
