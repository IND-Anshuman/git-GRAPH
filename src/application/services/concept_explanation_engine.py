"""Service engine for generating deterministic, auditable explanations for detected concepts."""

import uuid
from datetime import datetime
from typing import Any, Dict, List

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_explanation import ConceptExplanation
from src.domain.enums.entity_type import EntityType
from src.application.ports.unit_of_work import IUnitOfWork


class ConceptExplanationEngine:
    """Computes auditable explanations and footprints for a concept version without LLMs."""

    def explain_concept(
        self,
        uow: IUnitOfWork,
        concept_node: ConceptNode,
        concept_version: ConceptVersion,
        evidences: List[ConceptEvidence],
    ) -> ConceptExplanation:
        """
        Generate a deterministic ConceptExplanation for a ConceptVersion.

        Args:
            uow: Active Unit of Work.
            concept_node: The ConceptNode capability entity.
            concept_version: The specific version of the concept at a commit.
            evidences: Supporting evidence list.

        Returns:
            A ConceptExplanation domain entity.
        """
        # 1. Extract logic versions and evidences
        primary_triggers = []
        unique_files = set()
        class_entities = set()
        function_entities = set()
        loc_estimate = 0

        # We need the unique set of logic versions
        lv_ids = {ev.target_id for ev in evidences if ev.evidence_type == "LOGIC_VERSION"}

        for lv_id in lv_ids:
            lv = uow.logic_versions.get_by_id(lv_id)
            if not lv:
                continue

            sig = uow.logic_signatures.get_by_id(lv.logic_signature_id)
            pattern_id = sig.canonical_name if sig else "unknown"

            # Retrieve CodeEntity to identify its type and location
            entity = uow.code_entities.get_by_seid(lv.code_entity_seid)
            file_path = "unknown"
            start_line = 0
            end_line = 0

            # Get the version of the entity at this commit
            entity_ver = uow.entity_versions.get_latest_before_or_at(lv.code_entity_seid, lv.commit_hash)
            if entity_ver:
                file_path = entity_ver.file_path
                start_line = entity_ver.start_line
                end_line = entity_ver.end_line
            else:
                # Fallback to checking logic evidences
                logic_evs = uow.logic_evidence.get_by_logic_version(lv.id)
                if logic_evs:
                    file_path = logic_evs[0].file_path
                    start_line = min(ev.start_line for ev in logic_evs)
                    end_line = max(ev.end_line for ev in logic_evs)

            if file_path and file_path != "unknown":
                unique_files.add(file_path)

            if entity:
                # Categorize entity types
                if entity.entity_type in (EntityType.CLASS, EntityType.INTERFACE):
                    class_entities.add(entity.seid.value)
                elif entity.entity_type in (EntityType.FUNCTION, EntityType.METHOD):
                    function_entities.add(entity.seid.value)

            loc_estimate += max(0, end_line - start_line + 1)

            primary_triggers.append(
                {
                    "pattern_id": pattern_id,
                    "entity_seid": str(lv.code_entity_seid),
                    "file_path": file_path,
                    "confidence": float(lv.overall_confidence),
                }
            )

        file_count = len(unique_files)
        class_count = len(class_entities)
        function_count = len(function_entities)

        # 2. Build deterministic text summary
        confidence_percent = int(concept_version.confidence * 100)
        if concept_version.confidence >= 0.85:
            confidence_level = "high"
        elif concept_version.confidence >= 0.70:
            confidence_level = "moderate"
        else:
            confidence_level = "low"

        summary = (
            f"{concept_node.name} capability is verified with {confidence_level} confidence "
            f"({confidence_percent}%) based on {len(primary_triggers)} active behavior "
            f"patterns across {file_count} files."
        )

        detail = {
            "concept_id": str(concept_node.id),
            "name": concept_node.name,
            "commit_hash": concept_version.commit_hash,
            "confidence_score": float(concept_version.confidence),
            "explanation_summary": summary,
            "evidence_breakdown": {
                "primary_triggers": primary_triggers,
                "structural_footprint": {
                    "file_count": file_count,
                    "class_count": class_count,
                    "function_count": function_count,
                    "loc_estimate": loc_estimate,
                },
            },
        }

        # Determine explanation ID deterministically
        namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")
        explanation_id = uuid.uuid5(namespace, f"Explanation:{concept_version.id}")

        return ConceptExplanation(
            id=explanation_id,
            concept_version_id=concept_version.id,
            summary=summary,
            detail=detail,
            created_at=datetime.utcnow(),
        )
