"""Behavior Discovery Engine service to dynamically group method behaviors using CompositeBehaviorFingerprint."""

import re
import uuid
from typing import Any, Dict, List, Tuple, Optional
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.meta_ontology import MetaType, MetaDefinition
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.composite_fingerprint import CompositeBehaviorFingerprint
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry
from src.application.semantic.isr.canonical_entity import CanonicalEntity


class BehaviorDiscoveryEngine:
    """Traverses codebase behaviors, performs Jaccard similarity clustering, and registers candidate behavior types."""

    def __init__(
        self,
        uow: IUnitOfWork,
        schema_registry: SchemaRegistry,
        calibration_engine: ConfidenceCalibrationEngine,
    ):
        self.uow = uow
        self.schema_registry = schema_registry
        self.calibration_engine = calibration_engine

    def discover_behavior_clusters(
        self,
        repository_id: RepositoryId,
        entities: List[CanonicalEntity],
        similarity_threshold: float = 0.85,
    ) -> List[Tuple[MetaType, MetaDefinition]]:
        """Scans code methods, generates CompositeBehaviorFingerprint values, groups them, and registers candidates."""
        # Filter down to method/function/coroutine entities
        methods = [e for e in entities if e.entity_type.lower() in ("method", "function", "coroutine")]
        if not methods:
            methods = entities

        if not methods:
            return []

        # 1. Build composite fingerprints for each entity
        fingerprints = [self._build_fingerprint(m) for m in methods]

        # 2. Perform leader-based dynamic clustering
        clusters = self._cluster_fingerprints(fingerprints, similarity_threshold)

        discovered_candidates: List[Tuple[MetaType, MetaDefinition]] = []

        with self.uow:
            # 3. Process each cluster
            for idx, cluster_indices in enumerate(clusters):
                cluster_entities = [methods[i] for i in cluster_indices]
                
                # Determine a common suffix/prefix for the behavioral pattern
                candidate_name = self._determine_common_name(cluster_entities, idx)
                type_id = candidate_name.replace(" ", "")

                # Construct unified schema
                schema_definition = self._infer_schema_definition(cluster_entities, candidate_name)

                # Cohesion calibration
                cohesion_score = self._calculate_cohesion(fingerprints, cluster_indices)
                overall_confidence = self.calibration_engine.calibrate_joint_confidence(
                    evidence_scores=[cohesion_score, 0.85],
                    max_single_score=cohesion_score,
                )

                schema_definition["$confidence"] = overall_confidence

                # Semantic signature details
                semantic_signature = {
                    "common_suffix_or_prefix": self._find_common_substrings([e.name for e in cluster_entities]),
                    "entity_count": len(cluster_entities),
                    "aliases": [e.name for e in cluster_entities],
                }

                # 4. Register candidate via SchemaRegistry (category: BEHAVIORAL)
                meta_type = self.schema_registry.register_type(
                    type_id=type_id,
                    name=candidate_name,
                    category="BEHAVIORAL",
                    status="EXPERIMENTAL",
                )

                try:
                    meta_def = self.schema_registry.register_definition(
                        type_id=type_id,
                        schema_definition=schema_definition,
                        semantic_signature=semantic_signature,
                        version_string="1.0.0",
                    )
                    discovered_candidates.append((meta_type, meta_def))
                except ValueError:
                    # Definition already exists
                    latest = self.uow.meta_definitions.get_latest_definition(type_id)
                    if latest:
                        discovered_candidates.append((meta_type, latest))

            self.uow.commit()

        return discovered_candidates

    def _build_fingerprint(self, entity: CanonicalEntity) -> CompositeBehaviorFingerprint:
        """Constructs a CompositeBehaviorFingerprint from CanonicalEntity metadata fields."""
        meta = entity.metadata or {}

        # Safely parse AST shape
        ast_shape = str(meta.get("ast_shape", ""))

        # Calls signature mapping (strings or list of strings)
        calls = meta.get("call_signature", meta.get("calls", ""))
        if isinstance(calls, list):
            call_signature = ", ".join(calls)
        else:
            call_signature = str(calls)

        # Imports signature mapping
        imports = meta.get("import_signature", meta.get("imports", ""))
        if isinstance(imports, list):
            import_signature = ", ".join(imports)
        else:
            import_signature = str(imports)

        # Data flow signature mapping
        df = meta.get("data_flow_signature", meta.get("data_flow", ""))
        if isinstance(df, list):
            data_flow_signature = ", ".join(df)
        else:
            data_flow_signature = str(df)

        # Semantic tokens mapping
        tokens = meta.get("semantic_tokens", "")
        if isinstance(tokens, list):
            semantic_tokens = ", ".join(tokens)
        else:
            semantic_tokens = str(tokens)

        framework_context = str(meta.get("framework_context", ""))

        return CompositeBehaviorFingerprint(
            ast_shape=ast_shape,
            call_signature=call_signature,
            import_signature=import_signature,
            data_flow_signature=data_flow_signature,
            semantic_tokens=semantic_tokens,
            framework_context=framework_context,
        )

    def _cluster_fingerprints(
        self, fingerprints: List[CompositeBehaviorFingerprint], threshold: float
    ) -> List[List[int]]:
        """Groups fingerprint indices by pairwise CompositeBehaviorFingerprint similarity."""
        n = len(fingerprints)
        visited = [False] * n
        clusters = []

        for i in range(n):
            if visited[i]:
                continue
            cluster = [i]
            visited[i] = True
            for j in range(i + 1, n):
                if not visited[j]:
                    sim = fingerprints[i].calculate_similarity(fingerprints[j])
                    if sim >= threshold:
                        cluster.append(j)
                        visited[j] = True
            if len(cluster) >= 2:
                clusters.append(cluster)

        # Fallback to singletons if no clusters of size >= 2 were found
        if not clusters and fingerprints:
            clusters = [[i] for i in range(n)]

        return clusters

    def _determine_common_name(self, entities: List[CanonicalEntity], cluster_idx: int) -> str:
        """Extracts a common prefix or suffix to describe the behavior, falling back to a sequential name."""
        names = [e.name for e in entities]
        common = self._find_common_substrings(names)
        if common and len(common) >= 3:
            clean_name = re.sub(r"[^A-Za-z0-9]", "", common)
            if clean_name:
                return clean_name.capitalize()
        return f"DiscoveredBehavior{cluster_idx + 1}"

    def _find_common_substrings(self, strings: List[str]) -> str:
        """Finds the longest common prefix or suffix among a list of names."""
        if not strings:
            return ""
        rev_strings = [s[::-1] for s in strings]
        prefix = self._find_common_prefix(rev_strings)
        if prefix:
            return prefix[::-1]
        return self._find_common_prefix(strings)

    def _find_common_prefix(self, strings: List[str]) -> str:
        """Finds the longest common prefix among strings."""
        if not strings:
            return ""
        shortest = min(strings, key=len)
        for i, char in enumerate(shortest):
            for other in strings:
                if other[i] != char:
                    return shortest[:i]
        return shortest

    def _infer_schema_definition(self, entities: List[CanonicalEntity], type_name: str) -> Dict[str, Any]:
        """Infers a properties layout and title details based on attributes across entities."""
        properties = {
            "id": {"type": "string", "description": "Unique identifier of the entity"},
            "name": {"type": "string", "description": "Name of the entity"},
        }
        all_properties = {}
        for entity in entities:
            for key, val in entity.metadata.items():
                if key not in all_properties:
                    all_properties[key] = type(val).__name__

        for prop, type_name_val in all_properties.items():
            schema_type = "string"
            if type_name_val in ("int", "float"):
                schema_type = "number"
            elif type_name_val == "bool":
                schema_type = "boolean"
            elif type_name_val in ("dict", "list"):
                schema_type = "object"
            properties[prop] = {"type": schema_type}

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": type_name,
            "type": "object",
            "properties": properties,
            "required": ["id", "name"],
        }

    def _calculate_cohesion(
        self, fingerprints: List[CompositeBehaviorFingerprint], indices: List[int]
    ) -> float:
        """Calculates cluster cohesion (average pairwise similarity)."""
        cluster_fps = [fingerprints[i] for i in indices]
        if len(cluster_fps) < 2:
            return 1.0

        total_sim = 0.0
        count = 0
        n = len(cluster_fps)
        for i in range(n):
            for j in range(i + 1, n):
                total_sim += cluster_fps[i].calculate_similarity(cluster_fps[j])
                count += 1
        return total_sim / count if count > 0 else 1.0
