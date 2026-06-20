import uuid
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from typing import Any
from src.infrastructure.persistence.models.base import Base

class SADecision(Base):
    __tablename__ = "sa_decisions"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = sa.Column(sa.String(255), index=True, nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text)
    decision_type = sa.Column(sa.String(50), nullable=False)
    status = sa.Column(sa.String(50), nullable=False)
    confidence_score = sa.Column(sa.Float)
    first_seen_commit = sa.Column(sa.String(40))
    last_seen_commit = sa.Column(sa.String(40))
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())

class SADecisionVersion(Base):
    __tablename__ = "sa_decision_versions"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    version = sa.Column(sa.Integer, nullable=False)
    commit_hash = sa.Column(sa.String(40))
    confidence = sa.Column(sa.Float)
    supporting_evidence = sa.Column(sa.JSON)
    generated_at = sa.Column(sa.DateTime)

class SADecisionEvidence(Base):
    __tablename__ = "sa_decision_evidence"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    supporting_commits = sa.Column(sa.JSON)
    supporting_documents = sa.Column(sa.JSON)
    supporting_capabilities = sa.Column(sa.JSON)
    supporting_architecture_changes = sa.Column(sa.JSON)
    supporting_repository_events = sa.Column(sa.JSON)

class SADecisionImpact(Base):
    __tablename__ = "sa_decision_impacts"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    affected_capabilities = sa.Column(sa.JSON)
    affected_architectures = sa.Column(sa.JSON)
    affected_services = sa.Column(sa.JSON)
    affected_dependencies = sa.Column(sa.JSON)
    affected_ai_systems = sa.Column(sa.JSON)

class SADecisionImpactTimeline(Base):
    __tablename__ = "sa_decision_impact_timelines"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    entries = sa.Column(sa.JSON)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())

class SADecisionDependency(Base):
    __tablename__ = "sa_decision_dependencies"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    target_decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    relationship_type = sa.Column(sa.String(50))
    description = sa.Column(sa.Text)

class SADecisionConflict(Base):
    __tablename__ = "sa_decision_conflicts"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_a_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    decision_b_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    conflict_type = sa.Column(sa.String(50))
    description = sa.Column(sa.Text)
    severity = sa.Column(sa.Float)
    detected_at = sa.Column(sa.DateTime)

class SADecisionFitness(Base):
    __tablename__ = "sa_decision_fitness"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    longevity_score = sa.Column(sa.Float)
    stability_score = sa.Column(sa.Float)
    impact_score = sa.Column(sa.Float)
    adoption_score = sa.Column(sa.Float)
    success_rate = sa.Column(sa.Float)
    overall_fitness = sa.Column(sa.Float)
    evaluated_at = sa.Column(sa.DateTime)

class SADecisionSnapshot(Base):
    __tablename__ = "sa_decision_snapshots"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = sa.Column(sa.String(255), index=True, nullable=False)
    commit_hash = sa.Column(sa.String(40), index=True)
    decisions_json = sa.Column(sa.JSON)
    generated_at = sa.Column(sa.DateTime)

class SAIntent(Base):
    __tablename__ = "sa_intents"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = sa.Column(sa.String(255), index=True, nullable=False)
    name = sa.Column(sa.String(255))
    intent_type = sa.Column(sa.String(50))
    description = sa.Column(sa.Text)
    confidence_score = sa.Column(sa.Float)
    supporting_decisions = sa.Column(sa.JSON)
    first_seen_at = sa.Column(sa.DateTime)
    last_seen_at = sa.Column(sa.DateTime)

class SAIntentRelationship(Base):
    __tablename__ = "sa_intent_relationships"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    intent_id = sa.Column(sa.String(36), sa.ForeignKey("sa_intents.id"), nullable=False, index=True)
    decision_id = sa.Column(sa.String(36), sa.ForeignKey("sa_decisions.id"), nullable=False, index=True)
    relationship_type = sa.Column(sa.String(50))

class SARepositoryMemoryEvent(Base):
    __tablename__ = "sa_repository_memory_events"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = sa.Column(sa.String(255), index=True, nullable=False)
    event_type = sa.Column(sa.String(50))
    source = sa.Column(sa.String(50))
    commit_hash = sa.Column(sa.String(40))
    description = sa.Column(sa.Text)
    metadata_json = sa.Column(sa.JSON)
    occurred_at = sa.Column(sa.DateTime)

class SACausalRelationship(Base):
    __tablename__ = "sa_causal_relationships"
    id = sa.Column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_id = sa.Column(sa.String(36), index=True)
    repository_id = sa.Column(sa.String(255), index=True)
    cause_id = sa.Column(sa.String(36))
    effect_id = sa.Column(sa.String(36))
    cause_label = sa.Column(sa.String(255))
    effect_label = sa.Column(sa.String(255))
    relationship_type = sa.Column(sa.String(50))
    confidence = sa.Column(sa.Float)
    evidence = sa.Column(sa.JSON)
