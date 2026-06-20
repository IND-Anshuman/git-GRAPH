from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from .base import SQLAlchemyRepository
from src.infrastructure.persistence.models.decision_models import (
    SADecision, SADecisionVersion, SADecisionEvidence, SADecisionImpact,
    SADecisionImpactTimeline, SADecisionDependency, SADecisionConflict,
    SADecisionFitness, SADecisionSnapshot, SAIntent, SAIntentRelationship,
    SARepositoryMemoryEvent, SACausalRelationship
)

class SADecisionRepository(SQLAlchemyRepository[SADecision]):
    def __init__(self, session: Session):
        super().__init__(session, SADecision)

    def get_by_repository_id(self, repository_id: str) -> List[SADecision]:
        return self.session.query(SADecision).filter(SADecision.repository_id == repository_id).all()

class SADecisionVersionRepository(SQLAlchemyRepository[SADecisionVersion]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionVersion)

class SADecisionEvidenceRepository(SQLAlchemyRepository[SADecisionEvidence]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionEvidence)

class SADecisionImpactRepository(SQLAlchemyRepository[SADecisionImpact]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionImpact)

class SADecisionImpactTimelineRepository(SQLAlchemyRepository[SADecisionImpactTimeline]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionImpactTimeline)

class SADecisionDependencyRepository(SQLAlchemyRepository[SADecisionDependency]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionDependency)

class SADecisionConflictRepository(SQLAlchemyRepository[SADecisionConflict]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionConflict)

class SADecisionFitnessRepository(SQLAlchemyRepository[SADecisionFitness]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionFitness)

class SADecisionSnapshotRepository(SQLAlchemyRepository[SADecisionSnapshot]):
    def __init__(self, session: Session):
        super().__init__(session, SADecisionSnapshot)

class SAIntentRepository(SQLAlchemyRepository[SAIntent]):
    def __init__(self, session: Session):
        super().__init__(session, SAIntent)

class SAIntentRelationshipRepository(SQLAlchemyRepository[SAIntentRelationship]):
    def __init__(self, session: Session):
        super().__init__(session, SAIntentRelationship)

class SARepositoryMemoryEventRepository(SQLAlchemyRepository[SARepositoryMemoryEvent]):
    def __init__(self, session: Session):
        super().__init__(session, SARepositoryMemoryEvent)

class SACausalRelationshipRepository(SQLAlchemyRepository[SACausalRelationship]):
    def __init__(self, session: Session):
        super().__init__(session, SACausalRelationship)
