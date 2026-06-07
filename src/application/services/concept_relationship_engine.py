"""Service engine for inferring relationships between concepts."""

import uuid
from typing import Dict, List, Set, Tuple, Optional, Any

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.enums.concept_relationship_type import ConceptRelationshipType
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.services.historical_reconstruction import HistoricalReconstructionService


class ConceptRelationshipEngine:
    """Infers semantic and structural relationships between concepts using code-level dependencies."""

    def __init__(self, reconstruction_service: HistoricalReconstructionService) -> None:
        self.reconstruction_service = reconstruction_service

    def infer_relationships(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        commit_hash: str,
        detected_concepts: List[Tuple[ConceptNode, ConceptVersion, List[ConceptEvidence]]],
    ) -> List[ConceptRelationship]:
        """
        Infer concept relationships at a specific commit.

        Args:
            uow: Active Unit of Work.
            repository_id: The repository identifier.
            commit_hash: The Git commit hash.
            detected_concepts: List of concept detection tuples from the detection engine.

        Returns:
            A list of inferred ConceptRelationship entities.
        """
        if not detected_concepts:
            return []

        # 1. Map code entity SEIDs to Concept ID
        # Maps string(SEID) -> concept_node_id (UUID)
        entity_to_concept: Dict[str, uuid.UUID] = {}
        concept_by_id: Dict[uuid.UUID, ConceptNode] = {}
        concept_ver_by_node_id: Dict[uuid.UUID, ConceptVersion] = {}

        # Fetch active logic versions for mappings
        namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")

        for c_node, c_ver, ev_list in detected_concepts:
            concept_by_id[c_node.id] = c_node
            concept_ver_by_node_id[c_node.id] = c_ver

            for ev in ev_list:
                if ev.evidence_type == "LOGIC_VERSION":
                    l_ver = uow.logic_versions.get_by_id(ev.target_id)
                    if l_ver and l_ver.code_entity_seid:
                        entity_to_concept[str(l_ver.code_entity_seid.value)] = c_node.id

        # 2. Reconstruct base structural graph
        entities, relationships = self.reconstruction_service.reconstruct_graph_at_commit(
            uow, repository_id, commit_hash
        )

        # Build structural mapping helper: map child SEIDs to their parent classes/modules if needed
        # (Since relations might be defined at class level, and logic evidence at method level)
        child_to_parent: Dict[str, str] = {}
        for ent in entities:
            if ent.parent_seid:
                child_to_parent[str(ent.seid.value)] = str(ent.parent_seid.value)

        def resolve_concept(seid_str: str) -> Optional[uuid.UUID]:
            # Direct match
            if seid_str in entity_to_concept:
                return entity_to_concept[seid_str]
            # Try parent match
            parent = child_to_parent.get(seid_str)
            while parent:
                if parent in entity_to_concept:
                    return entity_to_concept[parent]
                parent = child_to_parent.get(parent)
            return None

        # 3. Track dependencies between concepts
        # concept_from -> concept_to -> list of relationship types/details
        concept_deps: Dict[uuid.UUID, Dict[uuid.UUID, List[str]]] = {}
        total_calls_from_concept: Dict[uuid.UUID, int] = {}

        for rel in relationships:
            src_concept = resolve_concept(str(rel.source_seid.value))
            tgt_concept = resolve_concept(str(rel.target_seid.value))

            if not src_concept or not tgt_concept or src_concept == tgt_concept:
                continue

            rel_type_str = rel.relationship_type.name if hasattr(rel.relationship_type, "name") else str(rel.relationship_type)

            if src_concept not in concept_deps:
                concept_deps[src_concept] = {}
            if tgt_concept not in concept_deps[src_concept]:
                concept_deps[src_concept][tgt_concept] = []

            concept_deps[src_concept][tgt_concept].append(rel_type_str)

            if rel_type_str in ("CALLS", "IMPORTS", "DEPENDS_ON"):
                total_calls_from_concept[src_concept] = total_calls_from_concept.get(src_concept, 0) + 1

        inferred_relationships: List[ConceptRelationship] = []

        # 4. Infer relationship types and confidence scores
        for src_id, targets in concept_deps.items():
            src_ver = concept_ver_by_node_id.get(src_id)
            if not src_ver:
                continue

            for tgt_id, rel_types in targets.items():
                tgt_ver = concept_ver_by_node_id.get(tgt_id)
                if not tgt_ver:
                    continue

                # Determine if it's IMPLEMENTS (contains inheritance links)
                is_implements = any(t in ("INHERITS", "IMPLEMENTS", "EXTENDS") for t in rel_types)

                # Compute dependency score
                calls_to_target = sum(1 for t in rel_types if t in ("CALLS", "IMPORTS", "DEPENDS_ON"))
                total_src_calls = total_calls_from_concept.get(src_id, 0)
                
                dep_score = (calls_to_target / total_src_calls) if total_src_calls > 0 else 0.0

                rel_type = ConceptRelationshipType.USES
                if is_implements:
                    rel_type = ConceptRelationshipType.IMPLEMENTS
                elif dep_score >= 0.15:
                    rel_type = ConceptRelationshipType.DEPENDS_ON
                elif any(t == "SUPPORTS" for t in rel_types):
                    rel_type = ConceptRelationshipType.SUPPORTS

                # Relationship confidence is computed from concept version confidences and coupling
                coupling_factor = max(dep_score, 0.50 if is_implements else 0.10)
                relationship_confidence = float(src_ver.confidence) * float(tgt_ver.confidence) * coupling_factor
                relationship_confidence = max(0.05, min(1.00, relationship_confidence))

                rel_id_str = f"{src_id}:{tgt_id}:{commit_hash}:{rel_type.value}"
                rel_id = uuid.uuid5(namespace, rel_id_str)

                inferred_relationships.append(
                    ConceptRelationship(
                        id=rel_id,
                        repository_id=repository_id,
                        commit_hash=commit_hash,
                        from_concept_id=src_id,
                        to_concept_id=tgt_id,
                        relationship_type=rel_type,
                        confidence=relationship_confidence,
                        metadata={
                            "coupling_ratio": dep_score,
                            "relationship_counts": len(rel_types),
                        },
                    )
                )

        return inferred_relationships
