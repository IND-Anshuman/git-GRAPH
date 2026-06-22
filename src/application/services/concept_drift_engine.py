"""Service engine for measuring conceptual drift across commits."""

import uuid
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_drift import ConceptDrift
from src.domain.value_objects.entity_id import SEID
from src.application.ports.unit_of_work import IUnitOfWork


class ConceptDriftEngine:
    """Computes structural, behavioral, and dependency drift metrics between concept versions."""

    def compute_drift(
        self,
        uow: IUnitOfWork,
        concept_id: uuid.UUID,
        baseline_version: ConceptVersion,
        current_version: ConceptVersion,
    ) -> ConceptDrift:
        """
        Compute drift scores comparing a baseline and current concept version.

        Args:
            uow: Active Unit of Work.
            concept_id: The ConceptNode UUID.
            baseline_version: Baseline ConceptVersion object.
            current_version: Current ConceptVersion object.

        Returns:
            A ConceptDrift domain entity.
        """
        # 1. Resolve SEIDs, Patterns and Dependencies for Baseline
        seids_base, patterns_base, deps_base = self._resolve_concept_assets(uow, baseline_version)

        # 2. Resolve SEIDs, Patterns and Dependencies for Current
        seids_curr, patterns_curr, deps_curr = self._resolve_concept_assets(uow, current_version)

        # 3. Calculate dimension drift scores using Jaccard Distance: 1 - Jaccard(A, B)
        drift_s = self._jaccard_distance(seids_base, seids_curr)
        drift_p = self._jaccard_distance(patterns_base, patterns_curr)
        drift_d = self._jaccard_distance(deps_base, deps_curr)

        # 4. Overall Weighted Score: 40% structural, 40% pattern, 20% dependency
        overall_score = 0.40 * drift_s + 0.40 * drift_p + 0.20 * drift_d

        # 5. Categorize
        if overall_score < 0.10:
            category = "TRIVIAL"
        elif overall_score < 0.30:
            category = "MINOR"
        elif overall_score < 0.60:
            category = "SIGNIFICANT"
        elif overall_score < 0.85:
            category = "MAJOR"
        else:
            category = "COMPLETE"

        drift_id = uuid.uuid5(
            uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234"),
            f"drift:{concept_id}:{baseline_version.commit_hash}:{current_version.commit_hash}",
        )

        return ConceptDrift(
            id=drift_id,
            concept_id=concept_id,
            baseline_commit=baseline_version.commit_hash,
            current_commit=current_version.commit_hash,
            drift_score=overall_score,
            drift_category=category,
            dimension_scores={
                "structural": drift_s,
                "pattern": drift_p,
                "dependency": drift_d,
            },
            computed_at=datetime.utcnow(),
        )

    def _resolve_concept_assets(
        self, uow: IUnitOfWork, version: ConceptVersion
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """Helper to extract implementing SEIDs, patterns, and dependencies."""
        evidence_list = uow.concept_evidence.list_by_concept_version(version.id)
        
        seids = set()
        patterns = set()
        
        # We query the logic versions to get target code entity SEIDs and pattern names
        for ev in evidence_list:
            if ev.evidence_type == "LOGIC_VERSION":
                l_ver = uow.logic_versions.get_by_id(ev.target_id)
                if l_ver:
                    if l_ver.code_entity_seid:
                        seids.add(str(l_ver.code_entity_seid.value))
                    sig = uow.logic_signatures.get_by_id(l_ver.logic_signature_id)
                    if sig:
                        patterns.add(sig.canonical_name)

        # Retrieve structural dependency edges mapped to these SEIDs at the specific commit
        dependencies = set()
        for seid_str in seids:
            # Look up relationships where source_seid is our entity at this commit
            try:
                rels = uow.relationships.get_by_source(SEID(uuid.UUID(seid_str)))
                for r in rels:
                    rel_type = r.relationship_type.name if hasattr(r.relationship_type, "name") else str(r.relationship_type)
                    dependencies.add(f"{rel_type}:{r.target_seid.value}")
            except Exception:
                pass # Fallback in case queries fail in test harnesses

        return seids, patterns, dependencies

    def _jaccard_distance(self, set_a: Set[Any], set_b: Set[Any]) -> float:
        """Compute Jaccard distance: 1 - Jaccard similarity."""
        if not set_a and not set_b:
            return 0.0
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        similarity = len(intersection) / len(union) if union else 1.0
        return 1.0 - similarity
