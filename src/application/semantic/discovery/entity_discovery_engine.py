"""Entity Discovery Engine service to dynamically discover semantic patterns and schemas."""

import re
from typing import Any, Dict, List, Tuple, Optional
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.meta_ontology import MetaType, MetaDefinition
from src.domain.enums.entity_type import EntityType
from src.domain.value_objects.repository_id import RepositoryId
from src.application.semantic.embedding.embedding_registry import EmbeddingRegistry
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.schema.schema_registry import SchemaRegistry


class EntityDiscoveryEngine:
    """Traverses codebase entities, performs vector clustering, and generates candidate meta-types and schemas."""

    def __init__(
        self,
        uow: IUnitOfWork,
        embedding_registry: EmbeddingRegistry,
        schema_registry: SchemaRegistry,
        calibration_engine: ConfidenceCalibrationEngine,
    ):
        self.uow = uow
        self.embedding_registry = embedding_registry
        self.schema_registry = schema_registry
        self.calibration_engine = calibration_engine

    def discover_semantic_types(
        self,
        repository_id: RepositoryId,
        similarity_threshold: float = 0.85,
    ) -> List[Tuple[MetaType, MetaDefinition]]:
        """Scans code entities, clusters them using embeddings, and generates candidates."""
        with self.uow:
            # 1. Fetch class entities
            all_entities = self.uow.code_entities.get_by_repository(
                repository_id, entity_type=EntityType.CLASS
            )
            if len(all_entities) < 2:
                # Fall back to function entities if classes are sparse
                all_entities = self.uow.code_entities.get_by_repository(repository_id)

            if len(all_entities) < 2:
                return []

            # 2. Get active embedding model, register a default one if none active
            active_model = self.embedding_registry.get_active_model()
            if not active_model:
                self.embedding_registry.register_model(
                    model_id="discovery-default-1",
                    model_name="Discovery Default Embedding",
                    provider="local",
                    dimensions=128,
                    distance_metric="cosine",
                    is_active=True,
                )
                self.embedding_registry.register_version(
                    model_id="discovery-default-1",
                    version_string="1.0.0",
                    configuration={},
                )
                active_model = self.embedding_registry.get_active_model()

            # 3. Compute simulated embeddings for each entity
            entity_embeddings = []
            valid_entities = []
            for entity in all_entities:
                try:
                    emb = self.embedding_registry.generate_simulated_embedding(entity.name)
                    entity_embeddings.append(emb)
                    valid_entities.append(entity)
                except Exception:
                    continue


            if not valid_entities:
                return []

            # 4. Perform dynamic clustering
            clusters = self._cluster_vectors(entity_embeddings, similarity_threshold)

            discovered_candidates = []

            # 5. Extract schema and register for each cluster
            for idx, cluster_indices in enumerate(clusters):
                cluster_entities = [valid_entities[i] for i in cluster_indices]
                
                # Determine common type name (e.g. Saga, Service, Controller)
                candidate_name = self._determine_common_name(cluster_entities, idx)
                type_id = candidate_name.replace(" ", "")

                # Construct schema definition by combining metadata / attributes
                schema_definition = self._infer_schema_definition(cluster_entities, candidate_name)
                
                # Infer semantic signature
                semantic_signature = {
                    "common_suffix_or_prefix": self._find_common_substrings([e.name for e in cluster_entities]),
                    "entity_count": len(cluster_entities),
                }

                # Calibrate confidence score
                # Evidence density is proportional to cluster cohesion
                cohesion_score = self._calculate_cohesion(
                    [entity_embeddings[i] for i in cluster_indices]
                )
                
                overall_confidence = self.calibration_engine.calibrate_joint_confidence(
                    evidence_scores=[cohesion_score, 0.8], # Cohesion and base similarity evidence
                    max_single_score=cohesion_score,
                )

                # Store confidence in metadata or signature
                schema_definition["$confidence"] = overall_confidence

                # 6. Register candidate via SchemaRegistry (default status: EXPERIMENTAL)
                meta_type = self.schema_registry.register_type(
                    type_id=type_id,
                    name=candidate_name,
                    category="STRUCTURAL",
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

    def _cluster_vectors(self, embeddings: List[List[float]], threshold: float) -> List[List[int]]:
        """Groups embedding indices by cosine similarity (Leader-based density clustering)."""
        # Try utilizing sklearn if available
        try:
            import numpy as np
            from sklearn.cluster import DBSCAN
            
            # Map cosine similarity to cosine distance (1 - similarity)
            X = np.array(embeddings)
            # Normalize to unit vectors
            norms = np.linalg.norm(X, axis=1, keepdims=True)
            X_normalized = np.where(norms > 0, X / norms, 0)
            
            # Distance matrix (1 - cosine similarity)
            # cosine similarity = A . B
            dist_matrix = 1.0 - np.dot(X_normalized, X_normalized.T)
            # Clip numerical precision errors
            dist_matrix = np.clip(dist_matrix, 0.0, 2.0)
            
            # DBSCAN with precomputed metric
            db = DBSCAN(eps=1.0 - threshold, min_samples=2, metric="precomputed")
            labels = db.fit_predict(dist_matrix)
            
            # Organize into clusters
            cluster_dict = {}
            for idx, label in enumerate(labels):
                if label == -1:
                    continue
                if label not in cluster_dict:
                    cluster_dict[label] = []
                cluster_dict[label].append(idx)
            return list(cluster_dict.values())
            
        except ImportError:
            # Pure-Python cosine-similarity leader-based clustering fallback
            n = len(embeddings)
            visited = [False] * n
            clusters = []

            def cosine_similarity(v1, v2):
                dot = sum(a * b for a, b in zip(v1, v2))
                return dot

            for i in range(n):
                if visited[i]:
                    continue
                cluster = [i]
                visited[i] = True
                for j in range(i + 1, n):
                    if not visited[j]:
                        sim = cosine_similarity(embeddings[i], embeddings[j])
                        if sim >= threshold:
                            cluster.append(j)
                            visited[j] = True
                if len(cluster) >= 2:
                    clusters.append(cluster)
            return clusters

    def _determine_common_name(self, entities: List[Any], cluster_idx: int) -> str:
        """Determines a common name pattern/suffix from cluster entities."""
        names = [e.name for e in entities]
        common = self._find_common_substrings(names)
        if common and len(common) >= 3:
            # Clean up non-alphanumeric characters
            clean_name = re.sub(r"[^A-Za-z0-9]", "", common)
            if clean_name:
                return clean_name.capitalize()
        return f"DiscoveredType {cluster_idx + 1}"

    def _find_common_substrings(self, strings: List[str]) -> str:
        """Finds the longest common suffix or prefix among strings."""
        if not strings:
            return ""
        
        # Longest Common Suffix
        rev_strings = [s[::-1] for s in strings]
        prefix = self._find_common_prefix(rev_strings)
        if prefix:
            return prefix[::-1]
        
        # Longest Common Prefix
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

    def _infer_schema_definition(self, entities: List[Any], type_name: str) -> Dict[str, Any]:
        """Infers a JSON Schema properties layout based on attributes across entities."""
        # Collate all property keys in metadata
        all_properties = {}
        for entity in entities:
            # Read attributes/metadata keys
            for key, val in entity.metadata.items():
                if key not in all_properties:
                    all_properties[key] = type(val).__name__

        # Build schema properties
        properties = {
            "id": {"type": "string", "description": "Unique identifier of the entity"},
            "name": {"type": "string", "description": "Name of the entity"},
        }
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

    def _calculate_cohesion(self, embeddings: List[List[float]]) -> float:
        """Calculates cluster cohesion (average pairwise cosine similarity)."""
        if len(embeddings) < 2:
            return 1.0
        
        total_sim = 0.0
        count = 0
        n = len(embeddings)
        
        def cosine_similarity(v1, v2):
            return sum(a * b for a, b in zip(v1, v2))

        for i in range(n):
            for j in range(i + 1, n):
                total_sim += cosine_similarity(embeddings[i], embeddings[j])
                count += 1
                
        return total_sim / count if count > 0 else 1.0
