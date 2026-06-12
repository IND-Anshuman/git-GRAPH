"""Service engine for detecting high-level concepts from low-level behaviors."""

import logging
import uuid
from typing import Dict, List, Tuple, Any

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.exceptions import ConceptDomainException
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.ontology_registry import ConceptOntologyRegistry

logger = logging.getLogger(__name__)


class ConceptDetectionEngine:
    """Computes deterministic concept classifications from behavior graph records."""

    MAX_CONCEPTS_PER_COMMIT = 500

    def __init__(self, ontology_registry: ConceptOntologyRegistry) -> None:
        self.ontology_registry = ontology_registry

    def detect_concepts(
        self, uow: IUnitOfWork, repository_id: RepositoryId, commit_hash: str
    ) -> List[Tuple[ConceptNode, ConceptVersion, List[ConceptEvidence]]]:
        """
        Detect concepts present in a repository at a specific commit.

        Args:
            uow: Active Unit of Work.
            repository_id: The repository identifier.
            commit_hash: The target Git commit hash.

        Returns:
            A list of tuples of (ConceptNode, ConceptVersion, List[ConceptEvidence]).
        """
        # 1. Fetch all logic signatures for the repository
        signatures = uow.logic_signatures.list_by_repository(repository_id)
        if not signatures:
            return []

        # 2. Fetch all logic versions at the given commit
        # Filter through logic_version_repo. We retrieve all logic versions for signatures at commit
        active_logic_versions = []
        signature_map = {sig.id: sig for sig in signatures}
        
        for sig in signatures:
            versions = uow.logic_versions.list_by_signature(sig.id)
            for v in versions:
                if v.commit_hash == commit_hash:
                    active_logic_versions.append(v)

        if not active_logic_versions:
            return []

        # Group logic versions and evidences by concept_id
        concept_groups: Dict[str, List[Tuple[Any, List[Any]]]] = {}
        for l_ver in active_logic_versions:
            sig = signature_map.get(l_ver.logic_signature_id)
            if not sig or not sig.ontology_node_id:
                continue

            # Lookup which concept ID this ontology pattern belongs to
            concept_id = self.ontology_registry.get_concept_by_pattern(sig.canonical_name)
            if not concept_id:
                # Fallback to direct mapping from ontology_node_id prefix
                concept_id = self.ontology_registry.get_concept_by_ontology_node_id(sig.ontology_node_id)
                if not concept_id:
                    logger.warning(f"Could not map ontology node id to a concept: {sig.ontology_node_id}")
                    continue

            # Check if concept is defined in registry
            concept_def = self.ontology_registry.get_concept(concept_id)
            if not concept_def:
                continue

            # Fetch supporting evidence
            evidence_list = uow.logic_evidence.get_by_logic_version(l_ver.id)

            if concept_id not in concept_groups:
                concept_groups[concept_id] = []
            concept_groups[concept_id].append((l_ver, evidence_list))

        # Safeguard limit check
        if len(concept_groups) > self.MAX_CONCEPTS_PER_COMMIT:
            raise ConceptDomainException(
                f"Concept explosion detected: {len(concept_groups)} concepts matched, "
                f"exceeding max limit of {self.MAX_CONCEPTS_PER_COMMIT}."
            )

        results = []
        for concept_id, items in concept_groups.items():
            concept_def = self.ontology_registry.get_concept(concept_id)
            
            # Verify if at least one required pattern is present
            required_patterns = concept_def["required_patterns"]
            matched_patterns = set()
            
            all_ver_evidences = []
            for l_ver, evs in items:
                sig = signature_map.get(l_ver.logic_signature_id)
                if sig:
                    matched_patterns.add(sig.canonical_name)

            # Check if we have at least one required pattern (or if required is empty)
            has_required = False
            if not required_patterns:
                has_required = True
            else:
                for req in required_patterns:
                    if req in matched_patterns:
                        has_required = True
                        break

            if not has_required:
                continue

            # Compute joint confidence score using Noisy-OR type-decay logic
            # Partition evidence by pattern/evidence type
            evidence_by_type: Dict[str, List[float]] = {}
            for l_ver, evs in items:
                sig = signature_map.get(l_ver.logic_signature_id)
                pattern_name = sig.canonical_name if sig else "unknown"
                
                # Add the version itself as evidence
                if pattern_name not in evidence_by_type:
                    evidence_by_type[pattern_name] = []
                evidence_by_type[pattern_name].append(l_ver.overall_confidence)

                # Add granular evidences
                for ev in evs:
                    ev_type = ev.evidence_type.value if hasattr(ev.evidence_type, "value") else str(ev.evidence_type)
                    if ev_type not in evidence_by_type:
                        evidence_by_type[ev_type] = []
                    evidence_by_type[ev_type].append(ev.confidence_contribution)

            # Calculate consolidated confidence per type
            type_confidences = []
            alpha = 0.5
            for ev_type, confs in evidence_by_type.items():
                confs.sort(reverse=True)
                prod = 1.0
                for idx, conf in enumerate(confs):
                    prod *= (1.0 - conf * (alpha ** idx))
                type_confidences.append(1.0 - prod)

            # Aggregated joint confidence Noisy-OR
            overall_prod = 1.0
            for tc in type_confidences:
                overall_prod *= (1.0 - tc)
            joint_conf = 1.0 - overall_prod

            # Clamp and calibrate using limits
            max_single = max([l_ver.overall_confidence for l_ver, _ in items])
            calibrated_conf = min(joint_conf, max_single + (1.0 - max_single) * 0.25)
            calibrated_conf = max(0.05, min(1.00, calibrated_conf))

            if calibrated_conf < concept_def["min_base_confidence"]:
                continue

            # Deterministic IDs
            # ConceptNode ID is UUID5 of repository_id + ontology_node_id
            namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")
            node_id_str = f"{repository_id.value}:{concept_id}"
            concept_node_id = uuid.uuid5(namespace, node_id_str)

            # Look up or create ConceptNode
            concept_node = uow.concept_nodes.get_by_id(concept_node_id)
            if not concept_node:
                concept_node = ConceptNode(
                    id=concept_node_id,
                    repository_id=repository_id,
                    ontology_node_id=concept_id,
                    name=concept_def["name"],
                    description=concept_def["description"],
                    is_system_defined=True,
                )

            # Determine concept version ordinal number
            existing_versions = uow.concept_versions.list_by_concept(concept_node_id)
            version_number = len(existing_versions) + 1

            # Generate ConceptVersion ID deterministically
            ver_id_str = f"{concept_node_id}:{commit_hash}"
            concept_version_id = uuid.uuid5(namespace, ver_id_str)

            concept_version = ConceptVersion(
                id=concept_version_id,
                concept_id=concept_node_id,
                commit_hash=commit_hash,
                version_number=version_number,
                confidence=calibrated_conf,
                is_active=True,
                metadata={
                    "evidence_types_count": len(type_confidences),
                    "logic_versions_count": len(items),
                },
            )

            # Generate ConceptEvidence entries
            concept_evidences = []
            for l_ver, evs in items:
                # 1. Evidence linking to LogicVersion
                ev_id = uuid.uuid5(namespace, f"{concept_version_id}:LogicVersion:{l_ver.id}")
                concept_evidences.append(
                    ConceptEvidence(
                        id=ev_id,
                        concept_version_id=concept_version_id,
                        evidence_type="LOGIC_VERSION",
                        target_id=l_ver.id,
                        confidence_contribution=l_ver.overall_confidence,
                        metadata={
                            "commit_hash": commit_hash,
                        },
                    )
                )

                # 2. Granular evidence lines if they exist
                for ev in evs:
                    ev_id_gran = uuid.uuid5(namespace, f"{concept_version_id}:LogicEvidence:{ev.id}")
                    concept_evidences.append(
                        ConceptEvidence(
                            id=ev_id_gran,
                            concept_version_id=concept_version_id,
                            evidence_type="LOGIC_EVIDENCE",
                            target_id=ev.id,
                            confidence_contribution=ev.confidence_contribution,
                            metadata={
                                "evidence_type": ev.evidence_type.value if hasattr(ev.evidence_type, "value") else str(ev.evidence_type),
                                "start_line": ev.start_line,
                                "end_line": ev.end_line,
                            },
                        )
                    )

            results.append((concept_node, concept_version, concept_evidences))

        return results
