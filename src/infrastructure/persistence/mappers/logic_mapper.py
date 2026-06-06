"""Data mapper converting between Phase 3 Domain Entities and SQLAlchemy Models."""

import json
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from src.domain.entities.behavior_drift import BehaviorDrift
from src.domain.entities.behavior_explanation import BehaviorExplanation, RuleVerdict
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.entities.logic_cluster import LogicCluster
from src.domain.entities.logic_evidence import LogicEvidence
from src.domain.entities.logic_signature import LogicSignature
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.logic_version import LogicVersion
from src.domain.entities.ontology_node import OntologyNode
from src.domain.enums.drift_category import DriftCategory
from src.domain.enums.evidence_type import EvidenceType
from src.domain.enums.language import SupportedLanguage
from src.domain.enums.transition_type import TransitionType
from src.domain.value_objects.confidence_breakdown import ConfidenceBreakdown
from src.domain.value_objects.drift_dimensions import DriftDimensions
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.value_objects.repository_id import RepositoryId
from src.infrastructure.persistence.models.logic_models import (
    BehaviorDriftModel,
    BehaviorExplanationModel,
    BehaviorPatternModel,
    LogicClusterModel,
    LogicEvidenceModel,
    LogicSignatureModel,
    LogicTransitionModel,
    LogicVersionModel,
    OntologyNodeModel,
)


class LogicMapper:
    """Mapper for Phase 3 entities and ORM models."""

    @staticmethod
    def _parse_enum(enum_cls, val):
        if val is None:
            return None
        if isinstance(val, enum_cls):
            return val
        try:
            return enum_cls(val)
        except ValueError:
            pass
        try:
            return enum_cls[val]
        except KeyError:
            pass
        return enum_cls(val)

    # ------------------------------------------------------------------ #
    # 1. OntologyNode Mappings                                           #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_ontology_node_model(entity: OntologyNode) -> OntologyNodeModel:
        return OntologyNodeModel(
            node_id=entity.id,
            name=entity.name,
            parent_node_id=entity.parent_id,
            domain=entity.domain,
            description=entity.description,
            ontology_version=entity.ontology_version,
            schema_version=entity.metadata.get("schema_version", "1.0"),
            is_leaf=entity.is_leaf,
            created_at=entity.loaded_at,
            updated_at=entity.loaded_at,
        )

    @staticmethod
    def to_ontology_node_entity(model: OntologyNodeModel) -> OntologyNode:
        return OntologyNode(
            id=model.node_id,
            name=model.name,
            parent_id=model.parent_node_id,
            domain=model.domain,
            description=model.description or "",
            ontology_version=model.ontology_version,
            is_leaf=model.is_leaf,
            metadata={"schema_version": model.schema_version},
            loaded_at=model.created_at,
        )

    # ------------------------------------------------------------------ #
    # 2. BehaviorPattern Mappings                                         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_behavior_pattern_model(entity: BehaviorPattern) -> BehaviorPatternModel:
        return BehaviorPatternModel(
            id=entity.id,
            pattern_id=entity.pattern_id,
            name=entity.name,
            pattern_version=entity.pattern_version,
            ontology_node_id=entity.ontology_node_id,
            base_confidence=entity.base_confidence,
            index_keys=entity.index_keys,
            rules=entity.rules,
            schema_version=entity.schema_version,
            is_active=entity.is_active,
            created_at=entity.loaded_at,
            updated_at=entity.loaded_at,
        )

    @staticmethod
    def to_behavior_pattern_entity(model: BehaviorPatternModel) -> BehaviorPattern:
        return BehaviorPattern(
            id=model.id,
            pattern_id=model.pattern_id,
            name=model.name,
            ontology_node_id=model.ontology_node_id,
            base_confidence=float(model.base_confidence),
            pattern_version=model.pattern_version,
            schema_version=model.schema_version,
            rules=model.rules,
            index_keys=model.index_keys,
            is_active=model.is_active,
            loaded_at=model.created_at,
        )

    # ------------------------------------------------------------------ #
    # 3. LogicSignature Mappings                                         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_logic_signature_model(entity: LogicSignature) -> LogicSignatureModel:
        # Retrieve properties from metadata if populated during extraction
        entity_seid = entity.metadata.get("entity_seid", str(uuid.uuid4()))
        entity_name = entity.metadata.get("entity_name", entity.canonical_name)
        entity_type = entity.metadata.get("entity_type", "FUNCTION")
        file_path = entity.metadata.get("file_path", "unknown")
        confidence = entity.metadata.get("overall_confidence", 1.0)

        return LogicSignatureModel(
            id=entity.id,
            repository_id=entity.repository_id.value,
            entity_seid=entity_seid,
            entity_name=entity_name,
            entity_type=entity_type,
            file_path=file_path,
            primary_ontology_node_id=entity.ontology_node_id,
            overall_confidence=confidence,
            metadata_=entity.metadata,
            first_seen_at=entity.created_at,
            last_seen_at=entity.created_at,
            created_at=entity.created_at,
            updated_at=entity.created_at,
        )

    @staticmethod
    def to_logic_signature_entity(model: LogicSignatureModel) -> LogicSignature:
        return LogicSignature(
            id=model.id,
            repository_id=RepositoryId(model.repository_id),
            canonical_name=model.entity_name,
            language=SupportedLanguage.PYTHON,  # Default, can be overridden by metadata
            ontology_node_id=model.primary_ontology_node_id,
            description=model.entity_name,
            created_at=model.created_at,
            metadata=model.metadata_,
        )

    # ------------------------------------------------------------------ #
    # 4. LogicVersion Mappings                                           #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_logic_version_model(entity: LogicVersion) -> LogicVersionModel:
        # Derive line range and complexity from metadata if available
        line_start = entity.metadata.get("line_start")
        line_end = entity.metadata.get("line_end")
        complexity = entity.metadata.get("complexity_score")
        index_keys = entity.metadata.get("index_keys", [])

        # Ensure entity_seid and is_primary are in metadata for queries
        meta = dict(entity.metadata)
        meta["entity_seid"] = str(entity.code_entity_seid.value)
        meta["is_primary"] = entity.is_primary

        return LogicVersionModel(
            id=entity.id,
            signature_id=entity.logic_signature_id,
            commit_hash=entity.commit_hash,
            version_number=entity.version_ordinal,
            confidence=entity.overall_confidence,
            index_keys=index_keys,
            ast_fingerprint=entity.fingerprint.composite,
            complexity_score=complexity,
            line_start=line_start,
            line_end=line_end,
            raw_source_hash=entity.fingerprint.structure_hash,
            metadata_=meta,
            observed_at=entity.created_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_logic_version_entity(model: LogicVersionModel) -> LogicVersion:
        # Reconstruct ConfidenceBreakdown from metadata if present
        breakdown = None
        if "confidence_breakdown" in model.metadata_:
            breakdown = ConfidenceBreakdown.from_dict(model.metadata_["confidence_breakdown"])

        # Reconstruct Fingerprint
        fingerprint = LogicFingerprint(
            structure_hash=model.raw_source_hash or "",
            dependency_hash=model.metadata_.get("dependency_hash", ""),
            behavioral_hash=model.metadata_.get("behavioral_hash", ""),
            composite=model.ast_fingerprint or "",
        )

        return LogicVersion(
            id=model.id,
            logic_signature_id=model.signature_id,
            code_entity_seid=SEID(uuid.UUID(model.metadata_.get("entity_seid")))
            if model.metadata_.get("entity_seid")
            else SEID.generate(),
            commit_hash=model.commit_hash,
            version_ordinal=model.version_number,
            fingerprint=fingerprint,
            overall_confidence=float(model.confidence),
            confidence_breakdown=breakdown,
            is_primary=model.metadata_.get("is_primary", True),
            metadata=model.metadata_,
            created_at=model.created_at,
        )

    # ------------------------------------------------------------------ #
    # 5. LogicEvidence Mappings                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_logic_evidence_model(entity: LogicEvidence) -> LogicEvidenceModel:
        meta = dict(entity.metadata)
        meta["file_path"] = entity.file_path
        meta["ast_node_type"] = entity.ast_node_type
        meta["call_chain"] = entity.call_chain
        meta["data_flow_path"] = entity.data_flow_path

        return LogicEvidenceModel(
            id=entity.id,
            version_id=entity.logic_version_id,
            evidence_type=entity.evidence_type.value,
            pattern_id=entity.matched_rule_id,
            matched_text=entity.matched_symbol,
            line_number=entity.start_line,
            column_offset=0,
            confidence=entity.confidence_contribution,
            weight=1.0,
            metadata_=meta,
            created_at=entity.detected_at,
        )

    @staticmethod
    def to_logic_evidence_entity(model: LogicEvidenceModel) -> LogicEvidence:
        return LogicEvidence(
            id=model.id,
            logic_version_id=model.version_id,
            evidence_type=LogicMapper._parse_enum(EvidenceType, model.evidence_type),
            file_path=model.metadata_.get("file_path", ""),
            start_line=model.line_number or 0,
            end_line=model.line_number or 0,
            ast_node_type=model.metadata_.get("ast_node_type"),
            matched_symbol=model.matched_text,
            matched_rule_id=model.pattern_id,
            call_chain=model.metadata_.get("call_chain", []),
            data_flow_path=model.metadata_.get("data_flow_path"),
            confidence_contribution=float(model.confidence),
            metadata=model.metadata_,
            detected_at=model.created_at,
        )

    # ------------------------------------------------------------------ #
    # 6. LogicTransition Mappings                                        #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_logic_transition_model(entity: LogicTransition) -> LogicTransitionModel:
        return LogicTransitionModel(
            id=entity.id,
            from_version_id=entity.from_logic_version_id,
            to_version_id=entity.to_logic_version_id,
            transition_type=entity.transition_type.value,
            from_commit_hash=entity.metadata.get("from_commit"),
            to_commit_hash=entity.metadata.get("to_commit", ""),
            similarity_score=entity.similarity_score,
            drift_magnitude=1.0 - entity.similarity_score,
            is_breaking_change=entity.similarity_score < 0.5,
            change_summary=entity.metadata.get("summary"),
            metadata_=entity.metadata,
            detected_at=entity.created_at,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_logic_transition_entity(model: LogicTransitionModel) -> LogicTransition:
        return LogicTransition(
            id=model.id,
            from_logic_version_id=model.from_version_id,
            to_logic_version_id=model.to_version_id,
            transition_type=LogicMapper._parse_enum(TransitionType, model.transition_type),
            similarity_score=float(model.similarity_score) if model.similarity_score is not None else 1.0,
            overall_confidence=float(model.metadata_.get("overall_confidence", 1.0)),
            metadata=model.metadata_,
            created_at=model.created_at,
        )

    # ------------------------------------------------------------------ #
    # 7. BehaviorExplanation Mappings                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_behavior_explanation_model(entity: BehaviorExplanation) -> BehaviorExplanationModel:
        # Serialize rule verdicts for storage
        detail_json = json.dumps([v.to_dict() for v in entity.rule_verdicts])

        # Ensure all structural attributes are in metadata for retrieval
        meta = dict(entity.metadata)
        meta["behavior_name"] = entity.behavior_name
        meta["ontology_path"] = entity.ontology_path
        meta["matched_pattern_ids"] = entity.matched_pattern_ids
        meta["is_stale"] = entity.is_stale
        if entity.confidence_breakdown:
            meta["confidence_breakdown"] = entity.confidence_breakdown.to_dict()

        return BehaviorExplanationModel(
            id=entity.id,
            version_id=entity.logic_version_id,
            explanation_type="narrative",
            summary=entity.evidence_summary,
            detail=detail_json,
            security_implications=entity.metadata.get("security_implications"),
            recommended_action=entity.metadata.get("recommended_action"),
            confidence=entity.overall_confidence,
            generated_by="logic_extraction_engine",
            metadata_=meta,
            created_at=entity.generated_at,
        )

    @staticmethod
    def to_behavior_explanation_entity(model: BehaviorExplanationModel) -> BehaviorExplanation:
        # Reconstruct verdicts
        verdicts = []
        if model.detail:
            try:
                raw_verdicts = json.loads(model.detail)
                verdicts = [RuleVerdict.from_dict(v) for v in raw_verdicts]
            except Exception:
                pass

        # Reconstruct breakdown
        breakdown = None
        if "confidence_breakdown" in model.metadata_:
            breakdown = ConfidenceBreakdown.from_dict(model.metadata_["confidence_breakdown"])

        return BehaviorExplanation(
            id=model.id,
            logic_version_id=model.version_id,
            behavior_name=model.metadata_.get("behavior_name", ""),
            ontology_path=model.metadata_.get("ontology_path", ""),
            overall_confidence=float(model.confidence),
            confidence_breakdown=breakdown or ConfidenceBreakdown.compute(1, 1, 1, 1, 1, 1),
            matched_pattern_ids=model.metadata_.get("matched_pattern_ids", []),
            evidence_summary=model.summary,
            rule_verdicts=verdicts,
            is_stale=model.metadata_.get("is_stale", False),
            generated_at=model.created_at,
            metadata=model.metadata_,
        )

    # ------------------------------------------------------------------ #
    # 8. BehaviorDrift Mappings                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_behavior_drift_model(entity: BehaviorDrift) -> BehaviorDriftModel:
        meta = dict(entity.metadata)
        meta["security_boundary_crossed"] = entity.security_boundary_crossed
        if entity.dimension_scores:
            meta["dimension_scores"] = entity.dimension_scores.to_dict()

        return BehaviorDriftModel(
            id=entity.id,
            transition_id=entity.logic_transition_id,
            baseline_version_id=entity.from_logic_version_id,
            current_version_id=entity.to_logic_version_id,
            drift_score=entity.drift_score,
            drift_category=entity.drift_category.value,
            ontology_shift=entity.ontology_changed,
            from_ontology_node_id=entity.metadata.get("from_ontology"),
            to_ontology_node_id=entity.metadata.get("to_ontology"),
            pattern_additions=entity.metadata.get("additions", {}),
            pattern_removals=entity.metadata.get("removals", {}),
            pattern_modifications=entity.metadata.get("modifications", {}),
            metadata_=meta,
            computed_at=entity.computed_at,
            created_at=entity.computed_at,
        )

    @staticmethod
    def to_behavior_drift_entity(model: BehaviorDriftModel) -> BehaviorDrift:
        # Reconstruct DriftDimensions
        dims_dict = model.metadata_.get("dimension_scores", {})
        dims = DriftDimensions(
            structural_drift=dims_dict.get("structural_drift", 0.0),
            dependency_drift=dims_dict.get("dependency_drift", 0.0),
            api_surface_drift=dims_dict.get("api_surface_drift", 0.0),
            control_flow_drift=dims_dict.get("control_flow_drift", 0.0),
            ontology_drift=dims_dict.get("ontology_drift", 0.0),
            security_drift=dims_dict.get("security_drift", 0.0),
        )

        return BehaviorDrift(
            id=model.id,
            logic_transition_id=model.transition_id,
            from_logic_version_id=model.baseline_version_id,
            to_logic_version_id=model.current_version_id,
            drift_score=float(model.drift_score),
            drift_category=LogicMapper._parse_enum(DriftCategory, model.drift_category),
            dimension_scores=dims,
            ontology_changed=model.ontology_shift,
            security_boundary_crossed=model.metadata_.get("security_boundary_crossed", False),
            computed_at=model.computed_at,
            metadata=model.metadata_,
        )

    # ------------------------------------------------------------------ #
    # 9. LogicCluster Mappings                                           #
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_logic_cluster_model(entity: LogicCluster) -> LogicClusterModel:
        return LogicClusterModel(
            id=entity.id,
            cluster_key=entity.name.lower().replace(" ", "_"),
            cluster_label=entity.name,
            ontology_node_id=entity.category,
            centroid_fingerprint=entity.metadata.get("centroid"),
            member_count=len(entity.logic_signature_ids),
            cohesion_score=entity.metadata.get("cohesion", 1.0),
            metadata_={
                "logic_signature_ids": [str(sid) for sid in entity.logic_signature_ids],
                **entity.metadata,
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def to_logic_cluster_entity(model: LogicClusterModel) -> LogicCluster:
        sig_ids = [
            uuid.UUID(sid)
            for sid in model.metadata_.get("logic_signature_ids", [])
        ]
        return LogicCluster(
            id=model.id,
            name=model.cluster_label or "",
            category=model.ontology_node_id or "",
            logic_signature_ids=sig_ids,
            metadata=model.metadata_,
        )
