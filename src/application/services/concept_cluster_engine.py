"""Service engine for clustering related concepts."""

import uuid
from typing import Dict, List, Set, Tuple

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_cluster import ConceptCluster
from src.domain.value_objects.repository_id import RepositoryId
from src.application.ports.unit_of_work import IUnitOfWork


class ConceptClusterEngine:
    """Groups granular concepts into high-level logical domains and dynamic structural cohorts."""

    DOMAIN_LABELS = {
        "security": "Identity & Access Management",
        "data_management": "Data Access Layer",
        "communication": "Integration & Messaging",
        "reliability": "Resilience & Fault Tolerance",
    }

    def compute_clusters(
        self,
        uow: IUnitOfWork,
        repository_id: RepositoryId,
        detected_concepts: List[Tuple[ConceptNode, ConceptVersion, List[ConceptEvidence]]],
    ) -> List[Tuple[ConceptCluster, List[uuid.UUID]]]:
        """
        Group concepts into domain clusters and structural cohorts.

        Returns:
            A list of tuples containing (ConceptCluster, List[ConceptNode IDs]).
        """
        if not detected_concepts:
            return []

        namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")
        concept_files: Dict[uuid.UUID, Set[str]] = {}
        concept_by_id: Dict[uuid.UUID, ConceptNode] = {}
        domain_groups: Dict[str, List[uuid.UUID]] = {}

        # 1. Gather files implementing each concept and group by static domain
        for c_node, c_ver, ev_list in detected_concepts:
            concept_by_id[c_node.id] = c_node
            
            # Resolve domain ID
            parts = c_node.ontology_node_id.split(".")
            domain_id = parts[0] if parts else "system"

            if domain_id not in domain_groups:
                domain_groups[domain_id] = []
            domain_groups[domain_id].append(c_node.id)

            files = set()
            for ev in ev_list:
                # Retrieve file_path from metadata
                file_path = ev.metadata.get("file_path")
                if file_path:
                    files.add(file_path)
                elif ev.evidence_type == "LOGIC_VERSION":
                    l_ver = uow.logic_versions.get_by_id(ev.target_id)
                    if l_ver and l_ver.logic_signature_id:
                        sig = uow.logic_signatures.get_by_id(l_ver.logic_signature_id)
                        if sig and sig.file_path:
                            files.add(sig.file_path)

            concept_files[c_node.id] = files

        clusters: List[Tuple[ConceptCluster, List[uuid.UUID]]] = []

        # 2. Build static domain clusters
        for domain_id, concept_ids in domain_groups.items():
            label = self.DOMAIN_LABELS.get(domain_id, f"{domain_id.title()} Domain")
            cluster_key = f"static_{domain_id}"
            cluster_id = uuid.uuid5(namespace, cluster_key)

            # Calculate average pairwise Jaccard cohesion for static clusters
            total_jaccard = 0.0
            pairs_count = 0
            for x in range(len(concept_ids)):
                for y in range(x + 1, len(concept_ids)):
                    fx = concept_files[concept_ids[x]]
                    fy = concept_files[concept_ids[y]]
                    inter = fx.intersection(fy)
                    uni = fx.union(fy)
                    total_jaccard += (len(inter) / len(uni)) if uni else 0.0
                    pairs_count += 1
            cohesion = (total_jaccard / pairs_count) if pairs_count > 0 else 1.0

            cluster = ConceptCluster(
                id=cluster_id,
                cluster_key=cluster_key,
                cluster_label=label,
                cohesion_score=cohesion,
                member_count=len(concept_ids),
            )
            clusters.append((cluster, concept_ids))

        # 3. Dynamic Structural Clustering (Jaccard Coupling Coefficient)
        # Check all pairs of concepts
        concept_list = list(concept_files.keys())
        visited: Set[uuid.UUID] = set()

        for i in range(len(concept_list)):
            c_a = concept_list[i]
            if c_a in visited:
                continue

            files_a = concept_files[c_a]
            if not files_a:
                continue

            dynamic_group = [c_a]

            for j in range(i + 1, len(concept_list)):
                c_b = concept_list[j]
                files_b = concept_files[c_b]
                if not files_b:
                    continue

                # Compute Jaccard
                intersection = files_a.intersection(files_b)
                union = files_a.union(files_b)
                jaccard = len(intersection) / len(union) if union else 0.0

                if jaccard >= 0.40:
                    dynamic_group.append(c_b)
                    visited.add(c_b)

            if len(dynamic_group) > 1:
                # Generate a dynamic cohort cluster
                node_names = sorted([concept_by_id[cid].name for cid in dynamic_group])
                label = " & ".join(node_names) + " Cohort"
                cluster_key = f"dynamic_" + "_".join([concept_by_id[cid].ontology_node_id.replace(".", "_") for cid in dynamic_group])
                
                # Truncate key if too long
                if len(cluster_key) > 120:
                    cluster_key = cluster_key[:120]
                
                cluster_id = uuid.uuid5(namespace, cluster_key)

                # Compute overall cohesion (average pairwise Jaccard)
                total_jaccard = 0.0
                pairs_count = 0
                for x in range(len(dynamic_group)):
                    for y in range(x + 1, len(dynamic_group)):
                        fx = concept_files[dynamic_group[x]]
                        fy = concept_files[dynamic_group[y]]
                        inter = fx.intersection(fy)
                        uni = fx.union(fy)
                        total_jaccard += (len(inter) / len(uni)) if uni else 0.0
                        pairs_count += 1

                cohesion = (total_jaccard / pairs_count) if pairs_count > 0 else 0.0

                cluster = ConceptCluster(
                    id=cluster_id,
                    cluster_key=cluster_key,
                    cluster_label=label,
                    cohesion_score=cohesion,
                    member_count=len(dynamic_group),
                )
                clusters.append((cluster, dynamic_group))

        return clusters
