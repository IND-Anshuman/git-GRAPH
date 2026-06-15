"""Discovery engine for automated capability intelligence extraction."""

import uuid
from typing import List, Dict, Set, Tuple, Any
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.capabilities.capability_candidate import CapabilityCandidate
from src.application.capabilities.capability_evidence import CapabilityEvidence

class CapabilityDiscoveryEngine:
    """The core engine that discovers capabilities using clustering, heuristics, and framework rules."""

    def discover_capabilities(self, uow: IUnitOfWork, repository_id: uuid.UUID) -> List[CapabilityCandidate]:
        """
        Main discovery entrypoint. Groups concepts, behaviors, flows, and entities
        into high-level system capabilities.
        """
        # 1. Fetch concept nodes from UOW
        from src.domain.value_objects.repository_id import RepositoryId
        repo_id_vo = RepositoryId(repository_id) if isinstance(repository_id, uuid.UUID) else repository_id
        concepts = uow.concept_nodes.list_by_repository(repo_id_vo) if hasattr(uow, "concept_nodes") else []
        candidates = []

        if concepts:
            # Cluster based on shared files/behaviors (Jaccard Similarity)
            concept_features: Dict[uuid.UUID, Set[str]] = {}
            concept_map: Dict[uuid.UUID, Any] = {}

            for c in concepts:
                concept_map[c.id] = c
                # Features are ontology name parts plus direct identifiers
                features = set(c.ontology_node_id.split("."))
                # Try getting associated files or evidence
                if hasattr(uow, "concept_versions") and hasattr(uow, "concept_evidence"):
                    versions = uow.concept_versions.list_by_concept(c.id)
                    if versions:
                        latest_version = versions[-1]
                        evidences = uow.concept_evidence.list_by_concept_version(latest_version.id)
                        for ev in evidences:
                            features.add(str(ev.target_id))
                            if ev.metadata and "file_path" in ev.metadata:
                                features.add(ev.metadata["file_path"])
                concept_features[c.id] = features

            # Build similarity edges
            edges: Dict[uuid.UUID, List[uuid.UUID]] = {c.id: [] for c in concepts}
            for i in range(len(concepts)):
                for j in range(i + 1, len(concepts)):
                    c1 = concepts[i]
                    c2 = concepts[j]
                    f1 = concept_features[c1.id]
                    f2 = concept_features[c2.id]
                    inter = f1.intersection(f2)
                    uni = f1.union(f2)
                    similarity = len(inter) / len(uni) if uni else 0.0

                    if similarity >= 0.25:  # Similarity threshold
                        edges[c1.id].append(c2.id)
                        edges[c2.id].append(c1.id)

            # Connected Components clustering
            components = self._find_connected_components(list(concept_map.keys()), edges)

            # Convert clusters to CapabilityCandidates
            for idx, comp in enumerate(components):
                comp_concepts = [concept_map[cid] for cid in comp]
                primary_concept = comp_concepts[0]
                
                # Dynamic naming based on primary concept's domain
                parts = primary_concept.ontology_node_id.split(".")
                name = parts[1].title() if len(parts) > 1 else primary_concept.name
                
                # Check for specific AI/Security/Business mappings
                cap_type = "TECHNICAL"
                if any("auth" in c.ontology_node_id.lower() or "security" in c.ontology_node_id.lower() for c in comp_concepts):
                    cap_type = "SECURITY"
                    name = "Authentication & Security"
                elif any("pay" in c.ontology_node_id.lower() or "checkout" in c.ontology_node_id.lower() for c in comp_concepts):
                    cap_type = "BUSINESS"
                    name = "Payment Processing"
                elif any("agent" in c.ontology_node_id.lower() or "retrieval" in c.ontology_node_id.lower() for c in comp_concepts):
                    cap_type = "AI"
                    name = "AI Agent Workloads"

                # Extract covered assets
                evidence = CapabilityEvidence(
                    concepts=[c.ontology_node_id for c in comp_concepts],
                    behaviors=[],
                    flows=[],
                    entities=[],
                    supporting_relationships=[],
                    confidence_breakdown={"jaccard_cohesion": 0.85}
                )

                candidate_id = uuid.uuid5(uuid.UUID("a7b3c291-5f2e-4d8a-b6c4-e1f0a9d2b5c8"), f"discovered_{idx}_{name}")
                candidates.append(CapabilityCandidate(
                    id=candidate_id,
                    name=name,
                    description=f"Automated capability discovered from concept cohort: {[c.name for c in comp_concepts]}",
                    confidence=0.90,
                    status="CANDIDATE",
                    evidence=evidence,
                    capability_type=cap_type
                ))
        else:
            # Robust fallback: check code entities and files to infer capabilities
            entities = uow.code_entities.get_by_repository(repo_id_vo) if hasattr(uow, "code_entities") else []
            if entities:
                # Group by namespace/module prefix (e.g. utils.auth -> Authentication, services.payment -> Payments)
                groups: Dict[str, List[Any]] = {}
                for ent in entities:
                    # Check module prefix
                    prefix = "core"
                    if ent.qualified_name:
                        parts = ent.qualified_name.split(".")
                        if len(parts) > 1:
                            prefix = parts[0]
                    if prefix not in groups:
                        groups[prefix] = []
                    groups[prefix].append(ent)

                for prefix, group_ents in groups.items():
                    name = f"{prefix.title()} Services"
                    cap_type = "TECHNICAL"
                    if "auth" in prefix.lower() or "sec" in prefix.lower():
                        cap_type = "SECURITY"
                        name = "Security & Access"
                    elif "pay" in prefix.lower() or "bill" in prefix.lower():
                        cap_type = "BUSINESS"
                        name = "Payments & Commerce"
                    elif "agent" in prefix.lower() or "model" in prefix.lower() or "ai" in prefix.lower():
                        cap_type = "AI"
                        name = "AI Agent Service"

                    evidence = CapabilityEvidence(
                        concepts=[],
                        behaviors=[],
                        flows=[],
                        entities=[ent.qualified_name for ent in group_ents],
                        supporting_relationships=[]
                    )
                    candidate_id = uuid.uuid5(uuid.UUID("a7b3c291-5f2e-4d8a-b6c4-e1f0a9d2b5c8"), f"fallback_{prefix}")
                    candidates.append(CapabilityCandidate(
                        id=candidate_id,
                        name=name,
                        description=f"Discovered by grouping namespace prefix: {prefix}",
                        confidence=0.75,
                        status="CANDIDATE",
                        evidence=evidence,
                        capability_type=cap_type
                    ))

        return candidates

    def _find_connected_components(self, nodes: List[uuid.UUID], edges: Dict[uuid.UUID, List[uuid.UUID]]) -> List[List[uuid.UUID]]:
        """Finds connected components in the graph."""
        visited = set()
        components = []
        for node in nodes:
            if node not in visited:
                component = []
                queue = [node]
                visited.add(node)
                while queue:
                    current = queue.pop(0)
                    component.append(current)
                    for neighbor in edges.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(component)
        return components
