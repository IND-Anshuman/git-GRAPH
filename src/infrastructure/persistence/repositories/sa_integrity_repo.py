"""SQLAlchemy implementation of IIntegrityRepository."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.domain.entities.integrity import IntegrityViolation, RepairAudit
from src.domain.repositories.integrity_repo import IIntegrityRepository
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.integrity_model import IntegrityViolationModel, RepairAuditModel
from src.infrastructure.persistence.mappers.domain_mapper import DomainMapper

class SAIntegrityRepository(IIntegrityRepository):
    """SQLAlchemy repository for integrity violations and repair audits."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_violation(self, violation: IntegrityViolation) -> None:
        model = DomainMapper.to_integrity_violation_model(violation)
        self.session.merge(model)

    def save_violations_batch(self, violations: List[IntegrityViolation]) -> None:
        for violation in violations:
            model = DomainMapper.to_integrity_violation_model(violation)
            self.session.merge(model)

    def get_violation_by_id(self, violation_id: uuid.UUID) -> Optional[IntegrityViolation]:
        model = self.session.get(IntegrityViolationModel, violation_id)
        if model:
            return DomainMapper.to_integrity_violation_entity(model)
        return None

    def list_violations_by_repository(self, repo_id: RepositoryId, unresolved_only: bool = False) -> List[IntegrityViolation]:
        stmt = select(IntegrityViolationModel).where(
            IntegrityViolationModel.repository_id == repo_id.value
        )
        if unresolved_only:
            stmt = stmt.where(IntegrityViolationModel.is_resolved == False)
        stmt = stmt.order_by(IntegrityViolationModel.detected_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_integrity_violation_entity(m) for m in models]

    def save_repair_audit(self, audit: RepairAudit) -> None:
        model = DomainMapper.to_repair_audit_model(audit)
        self.session.merge(model)

    def list_repair_audits_by_repository(self, repo_id: RepositoryId) -> List[RepairAudit]:
        stmt = select(RepairAuditModel).where(
            RepairAuditModel.repository_id == repo_id.value
        ).order_by(RepairAuditModel.executed_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [DomainMapper.to_repair_audit_entity(m) for m in models]
