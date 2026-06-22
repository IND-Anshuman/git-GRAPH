"""Use case for retrieving repository-wide behavior logic evolution timeline."""

import uuid
from typing import Callable, List, Dict, Any

from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects.repository_id import RepositoryId


class GetLogicTimelineUseCase:
    """Retrieves all logic signatures, versions, transitions, and explanations for a repository."""

    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self.uow_factory = uow_factory

    def execute(self, repository_id_str: str) -> Dict[str, Any]:
        """Fetch all logic structures and group them by signature."""
        repo_id = RepositoryId(uuid.UUID(repository_id_str))

        with self.uow_factory() as uow:
            # 1. Fetch all signatures
            signatures = uow.logic_signatures.list_by_repository(repo_id)
            signatures_data = []

            for sig in signatures:
                # 2. Fetch versions and transitions
                versions = uow.logic_versions.list_by_signature(sig.id)
                transitions = uow.logic_transitions.list_by_signature(sig.id)

                versions_data = []
                explanations_data = []
                evidence_data = []
                drift_data = []
                transitions_data = []

                for v in versions:
                    # Confidence breakdown
                    cb = None
                    if v.confidence_breakdown:
                        cb = {
                            "overall_confidence": v.confidence_breakdown.overall_confidence,
                            "ast_confidence": v.confidence_breakdown.ast_confidence,
                            "dependency_confidence": v.confidence_breakdown.dependency_confidence,
                            "data_flow_confidence": v.confidence_breakdown.data_flow_confidence,
                            "pattern_confidence": v.confidence_breakdown.pattern_confidence,
                            "structural_confidence": v.confidence_breakdown.structural_confidence,
                            "evidence_count": v.confidence_breakdown.evidence_count,
                        }

                    versions_data.append({
                        "id": str(v.id),
                        "logic_signature_id": str(v.logic_signature_id),
                        "code_entity_seid": str(v.code_entity_seid),
                        "commit_hash": v.commit_hash,
                        "version_ordinal": v.version_ordinal,
                        "fingerprint": {
                            "structure_hash": v.fingerprint.structure_hash,
                            "dependency_hash": v.fingerprint.dependency_hash,
                            "behavioral_hash": v.fingerprint.behavioral_hash,
                            "composite": v.fingerprint.composite,
                        },
                        "overall_confidence": v.overall_confidence,
                        "confidence_breakdown": cb,
                        "is_primary": v.is_primary,
                        "metadata": v.metadata,
                        "created_at": v.created_at,
                    })

                    # Explanation
                    exp = uow.behavior_explanations.get_by_logic_version(v.id)
                    if exp:
                        exp_cb = {
                            "overall_confidence": exp.confidence_breakdown.overall_confidence,
                            "ast_confidence": exp.confidence_breakdown.ast_confidence,
                            "dependency_confidence": exp.confidence_breakdown.dependency_confidence,
                            "data_flow_confidence": exp.confidence_breakdown.data_flow_confidence,
                            "pattern_confidence": exp.confidence_breakdown.pattern_confidence,
                            "structural_confidence": exp.confidence_breakdown.structural_confidence,
                            "evidence_count": exp.confidence_breakdown.evidence_count,
                        }

                        verdicts = [
                            {
                                "rule_id": verdict.rule_id,
                                "rule_description": verdict.rule_description,
                                "passed": verdict.passed,
                                "contribution": verdict.contribution,
                                "evidence_ref": str(verdict.evidence_ref) if verdict.evidence_ref else None,
                            }
                            for verdict in exp.rule_verdicts
                        ]

                        explanations_data.append({
                            "id": str(exp.id),
                            "logic_version_id": str(exp.logic_version_id),
                            "behavior_name": exp.behavior_name,
                            "ontology_path": exp.ontology_path,
                            "overall_confidence": exp.overall_confidence,
                            "confidence_breakdown": exp_cb,
                            "matched_pattern_ids": exp.matched_pattern_ids,
                            "evidence_summary": exp.evidence_summary,
                            "rule_verdicts": verdicts,
                            "is_stale": exp.is_stale,
                            "generated_at": exp.generated_at,
                            "metadata": exp.metadata,
                        })

                    # Evidence
                    evidence = uow.logic_evidence.get_by_logic_version(v.id)
                    for ev in evidence:
                        evidence_data.append({
                            "id": str(ev.id),
                            "logic_version_id": str(ev.logic_version_id),
                            "evidence_type": ev.evidence_type.value if hasattr(ev.evidence_type, "value") else str(ev.evidence_type),
                            "file_path": ev.file_path,
                            "start_line": ev.start_line,
                            "end_line": ev.end_line,
                            "ast_node_type": ev.ast_node_type,
                            "matched_symbol": ev.matched_symbol,
                            "matched_rule_id": ev.matched_rule_id,
                            "call_chain": ev.call_chain,
                            "data_flow_path": ev.data_flow_path,
                            "confidence_contribution": ev.confidence_contribution,
                            "metadata": ev.metadata,
                            "detected_at": ev.detected_at,
                        })

                # Transitions and Drift
                for trans in transitions:
                    transitions_data.append({
                        "id": str(trans.id),
                        "from_logic_version_id": str(trans.from_logic_version_id) if trans.from_logic_version_id else None,
                        "to_logic_version_id": str(trans.to_logic_version_id) if trans.to_logic_version_id else None,
                        "transition_type": trans.transition_type.value if hasattr(trans.transition_type, "value") else str(trans.transition_type),
                        "similarity_score": trans.similarity_score,
                        "overall_confidence": trans.overall_confidence,
                        "metadata": trans.metadata,
                        "created_at": trans.created_at,
                    })

                    # Drift
                    drift = uow.behavior_drift.get_by_transition(trans.id)
                    if drift:
                        drift_data.append({
                            "id": str(drift.id),
                            "logic_transition_id": str(drift.logic_transition_id),
                            "from_logic_version_id": str(drift.from_logic_version_id),
                            "to_logic_version_id": str(drift.to_logic_version_id),
                            "drift_score": drift.drift_score,
                            "drift_category": drift.drift_category.value if hasattr(drift.drift_category, "value") else str(drift.drift_category),
                            "dimension_scores": {
                                "structural_drift": drift.dimension_scores.structural_drift,
                                "dependency_drift": drift.dimension_scores.dependency_drift,
                                "api_surface_drift": drift.dimension_scores.api_surface_drift,
                                "control_flow_drift": drift.dimension_scores.control_flow_drift,
                                "ontology_drift": drift.dimension_scores.ontology_drift,
                                "security_drift": drift.dimension_scores.security_drift,
                            },
                            "ontology_changed": drift.ontology_changed,
                            "security_boundary_crossed": drift.security_boundary_crossed,
                            "computed_at": drift.computed_at,
                            "metadata": drift.metadata,
                        })

                signatures_data.append({
                    "signature": {
                        "id": str(sig.id),
                        "repository_id": str(sig.repository_id.value),
                        "canonical_name": sig.canonical_name,
                        "language": sig.language.name if hasattr(sig.language, "name") else str(sig.language),
                        "ontology_node_id": sig.ontology_node_id,
                        "description": sig.description,
                        "created_at": sig.created_at,
                        "metadata": sig.metadata,
                    },
                    "versions": versions_data,
                    "transitions": transitions_data,
                    "explanations": explanations_data,
                    "evidence": evidence_data,
                    "drift": drift_data,
                })

            return {
                "repository_id": repository_id_str,
                "signatures": signatures_data,
            }
