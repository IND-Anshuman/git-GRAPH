"""Concept Discovery Engine to identify latent concept candidates from behavioral networks."""

import uuid
import re
from typing import Any, Dict, List, Tuple, Optional, Set
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.concept_candidate import ConceptCandidate
from src.domain.value_objects.candidate_evidence import CandidateEvidence
from src.domain.value_objects.repository_id import RepositoryId
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.domain.entities.meta_ontology import MetaType


class ConceptDiscoveryEngine:
    """Discovers high-level semantic concepts, computes Placement Scores, and registers candidates."""

    def __init__(
        self,
        uow: IUnitOfWork,
        schema_registry: SchemaRegistry,
        embedding_registry: EmbeddingRegistry,
        calibration_engine: ConfidenceCalibrationEngine,
    ):
        self.uow = uow
        self.schema_registry = schema_registry
        self.embedding_registry = embedding_registry
        self.calibration_engine = calibration_engine

    def discover_concept_candidates(
        self,
        repository_id: RepositoryId,
        similarity_threshold: float = 0.80,
    ) -> List[ConceptCandidate]:
        """Scans the behavioral co-occurrences, clusters them, calculates placement scores, and registers candidates."""
        candidates: List[ConceptCandidate] = []

        with self.uow:
            # 1. Fetch all logic signatures (representing behaviors)
            signatures = self.uow.logic_signatures.list_by_repository(repository_id)
            if len(signatures) < 2:
                return []

            # 2. Build co-occurrence map (group by file or namespace)
            file_to_behaviors: Dict[str, List[Any]] = {}
            for sig in signatures:
                file_path = sig.file_path
                if file_path not in file_to_behaviors:
                    file_to_behaviors[file_path] = []
                file_to_behaviors[file_path].append(sig)

            # 3. Simple co-occurrence clustering (Leader-based over Jaccard behavior overlap)
            # Find groups of behaviors that often appear together in the same files
            behavior_sets = []
            for file_path, sigs in file_to_behaviors.items():
                if len(sigs) >= 2:
                    behavior_sets.append(sigs)

            if not behavior_sets:
                # Fallback to group by parent directory
                dir_to_behaviors: Dict[str, List[Any]] = {}
                for sig in signatures:
                    parent_dir = "/".join(sig.file_path.split("/")[:-1])
                    if parent_dir not in dir_to_behaviors:
                        dir_to_behaviors[parent_dir] = []
                    dir_to_behaviors[parent_dir].append(sig)
                behavior_sets = [sigs for sigs in dir_to_behaviors.values() if len(sigs) >= 2]

            if not behavior_sets:
                return []

            # Cluster co-occurring signatures
            clusters = self._cluster_co_occurrences(behavior_sets, similarity_threshold)

            # 4. Process each cluster to form a ConceptCandidate
            for idx, cluster_sigs in enumerate(clusters):
                candidate_name = self._determine_common_name(cluster_sigs, idx)
                candidate_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"concept-candidate:{repository_id.value}:{candidate_name}")

                # Gather supporting behaviors, relationships, and entities
                supporting_entities = list(set(str(sig.entity_seid) for sig in cluster_sigs))
                supporting_behaviors = list(set(sig.canonical_name for sig in cluster_sigs))
                
                # Fetch relationships for these entities
                supporting_relationships: List[str] = []
                for entity_id in supporting_entities:
                    try:
                        rels = self.uow.relationships.get_by_entity(entity_id)
                        supporting_relationships.extend(str(r.id) for r in rels)
                    except Exception:
                        continue
                supporting_relationships = list(set(supporting_relationships))

                # Build candidate evidence
                evidence = CandidateEvidence(
                    supporting_entities=supporting_entities,
                    supporting_relationships=supporting_relationships,
                    supporting_behaviors=supporting_behaviors,
                    confidence_breakdown={"co_occurrence_cohesion": 0.90},
                )

                # 5. Calculate parent placement candidate using the 40/30/20/10 weighted formula
                parent_node_id, placement_score = self._calculate_placement(
                    candidate_name, cluster_sigs, supporting_relationships
                )

                # Calibrate confidence
                overall_confidence = self.calibration_engine.calibrate_joint_confidence(
                    evidence_scores=[placement_score, 0.80],
                    max_single_score=placement_score,
                )

                candidate = ConceptCandidate(
                    id=candidate_id,
                    name=candidate_name,
                    confidence=overall_confidence,
                    evidence=evidence,
                    ontology_parent_candidate=parent_node_id,
                    status="CANDIDATE",
                )
                candidate.validate()
                candidates.append(candidate)

                # 6. Stage as a CONCEPTUAL MetaType and MetaDefinition in schema registry
                self.schema_registry.register_type(
                    type_id=str(candidate_id),
                    name=candidate_name,
                    category="CONCEPTUAL",
                    status="CANDIDATE",
                )
                
                schema_def = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "title": candidate_name,
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "ontology_parent": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                    "required": ["name"],
                }

                semantic_sig = {
                    "repository_id": str(repository_id.value),
                    "ontology_parent_candidate": parent_node_id,
                    "evidence": evidence.to_dict(),
                    "placement_score": placement_score,
                }

                try:
                    self.schema_registry.register_definition(
                        type_id=str(candidate_id),
                        schema_definition=schema_def,
                        semantic_signature=semantic_sig,
                        version_string="1.0.0",
                    )
                except ValueError:
                    pass

            self.uow.commit()

        return candidates

    def _cluster_co_occurrences(
        self, behavior_sets: List[List[Any]], threshold: float
    ) -> List[List[Any]]:
        """Clusters co-occurring behavior signature groups using Jaccard similarity."""
        sig_map = {}
        for bs in behavior_sets:
            for sig in bs:
                sig_map[sig.id] = sig

        unique_groups: List[Set[Any]] = []
        for bs in behavior_sets:
            s = set(sig.id for sig in bs)
            # Merge overlapping sets if they share behaviors
            merged = False
            for ug in unique_groups:
                intersection = len(s.intersection(ug))
                union = len(s.union(ug))
                jaccard = intersection / union if union > 0 else 0.0
                if jaccard >= threshold:
                    ug.update(s)
                    merged = True
                    break
            if not merged:
                unique_groups.append(s)

        return [[sig_map[sid] for sid in ug] for ug in unique_groups]

    def _determine_common_name(self, signatures: List[Any], idx: int) -> str:
        """Determines a common name pattern from logic signature names."""
        names = [sig.entity_name for sig in signatures]
        # Look for common prefix or suffix
        common = self._find_common_substrings(names)
        if common and len(common) >= 3:
            clean_name = re.sub(r"[^A-Za-z0-9]", "", common)
            if clean_name:
                return f"{clean_name.capitalize()}Concept"
        return f"DiscoveredConcept{idx + 1}"

    def _find_common_substrings(self, strings: List[str]) -> str:
        if not strings:
            return ""
        rev_strings = [s[::-1] for s in strings]
        prefix = self._find_common_prefix(rev_strings)
        if prefix:
            return prefix[::-1]
        return self._find_common_prefix(strings)

    def _find_common_prefix(self, strings: List[str]) -> str:
        if not strings:
            return ""
        shortest = min(strings, key=len)
        for i, char in enumerate(shortest):
            for other in strings:
                if other[i] != char:
                    return shortest[:i]
        return shortest

    def _calculate_placement(
        self,
        candidate_name: str,
        signatures: List[Any],
        relationships: List[str],
    ) -> Tuple[str, float]:
        """Calculates placement parent node using weighted Concept Placement Score.

        Score = 0.40 * OntologySimilarity + 0.30 * BehaviorOverlap + 0.20 * RelationshipSimilarity + 0.10 * EmbeddingSimilarity
        """
        # Fetch static ontology nodes to check against
        ontology_nodes = self.uow.ontology_nodes.list_all()
        if not ontology_nodes:
            return "root", 0.50

        candidate_tokens = set(t.lower() for t in re.split(r"[^a-zA-Z0-9]+", candidate_name) if t)

        best_parent = "root"
        best_score = 0.0

        for node in ontology_nodes:
            # 1. Ontology Similarity (Name token Jaccard)
            node_tokens = set(t.lower() for t in re.split(r"[^a-zA-Z0-9]+", node.name) if t)
            node_tokens.update(t.lower() for t in node.id.split(".") if t)
            
            if not candidate_tokens or not node_tokens:
                ontology_sim = 0.0
            else:
                ontology_sim = len(candidate_tokens.intersection(node_tokens)) / len(
                    candidate_tokens.union(node_tokens)
                )

            # 2. Behavior Overlap
            # Compare what logic signatures belong to this ontology node vs candidate signatures
            node_signatures = self.uow.logic_signatures.list_by_ontology_node(node.id)
            node_behaviors = set(ns.canonical_name for ns in node_signatures)
            candidate_behaviors = set(sig.canonical_name for sig in signatures)
            
            if not node_behaviors and not candidate_behaviors:
                behavior_sim = 1.0
            elif not node_behaviors or not candidate_behaviors:
                behavior_sim = 0.0
            else:
                behavior_sim = len(candidate_behaviors.intersection(node_behaviors)) / len(
                    candidate_behaviors.union(node_behaviors)
                )

            # 3. Relationship Similarity
            # Match interaction graph properties
            relationship_sim = 0.50  # Default baseline overlap

            # 4. Embedding Similarity (Using EmbeddingRegistry as tie-breaker)
            try:
                emb_c = self.embedding_registry.generate_simulated_embedding(candidate_name)
                emb_n = self.embedding_registry.generate_simulated_embedding(node.name)
                # Cosine similarity (dot product of normalized vectors)
                embedding_sim = sum(x * y for x, y in zip(emb_c, emb_n))
            except Exception:
                embedding_sim = 0.0

            # Weighted Formula
            score = (
                0.40 * ontology_sim
                + 0.30 * behavior_sim
                + 0.20 * relationship_sim
                + 0.10 * embedding_sim
            )

            if score > best_score:
                best_score = score
                best_parent = node.id

        return best_parent, best_score
