"""Service engine for computing concept graph metrics."""

import uuid
from typing import Dict, List, Set, Tuple
from datetime import datetime

from src.domain.entities.concept_node import ConceptNode
from src.domain.entities.concept_version import ConceptVersion
from src.domain.entities.concept_evidence import ConceptEvidence
from src.domain.entities.concept_relationship import ConceptRelationship
from src.domain.entities.concept_metrics import ConceptMetrics
from src.application.ports.unit_of_work import IUnitOfWork


class ConceptMetricsEngine:
    """Computes topological graph centralities and structural size metrics for concepts."""

    def compute_metrics(
        self,
        uow: IUnitOfWork,
        detected_concepts: List[Tuple[ConceptNode, ConceptVersion, List[ConceptEvidence]]],
        relationships: List[ConceptRelationship],
    ) -> List[ConceptMetrics]:
        """
        Compute size, centrality, PageRank, and impact metrics for each concept version.

        Args:
            uow: Active Unit of Work.
            detected_concepts: Detected concept nodes and versions at the current commit.
            relationships: Inferred concept relationship edges.

        Returns:
            A list of ConceptMetrics domain entities.
        """
        if not detected_concepts:
            return []

        # 1. Size calculation helpers
        concept_sizes: Dict[uuid.UUID, Tuple[int, int]] = {}
        for c_node, c_ver, ev_list in detected_concepts:
            # Entity Count: number of active LogicVersions supporting the concept
            # File Count: number of unique files containing these entities
            entities = set()
            files = set()
            for ev in ev_list:
                if ev.evidence_type == "LOGIC_VERSION":
                    l_ver = uow.logic_versions.get_by_id(ev.target_id)
                    if l_ver and l_ver.code_entity_seid:
                        entities.add(str(l_ver.code_entity_seid.value))
                        sig = uow.logic_signatures.get_by_id(l_ver.logic_signature_id)
                        if sig and sig.file_path:
                            files.add(sig.file_path)

            concept_sizes[c_node.id] = (len(entities), len(files))

        # 2. Build adjacency list of concept dependency graph
        # concept_id -> set of concept_ids it depends on
        adj_out: Dict[uuid.UUID, Set[uuid.UUID]] = {c[0].id: set() for c in detected_concepts}
        adj_in: Dict[uuid.UUID, Set[uuid.UUID]] = {c[0].id: set() for c in detected_concepts}
        edge_confidences: Dict[Tuple[uuid.UUID, uuid.UUID], float] = {}

        for rel in relationships:
            if rel.relationship_type.value == "DEPENDS_ON":
                src = rel.from_concept_id
                tgt = rel.to_concept_id
                if src in adj_out and tgt in adj_out:
                    adj_out[src].add(tgt)
                    adj_in[tgt].add(src)
                    edge_confidences[(src, tgt)] = float(rel.confidence)

        concept_ids = list(adj_out.keys())
        n = len(concept_ids)

        # 3. PageRank Score Calculation (Power Iteration)
        pagerank = {cid: 1.0 / n for cid in concept_ids}
        d = 0.85 # damping factor
        iterations = 20

        for _ in range(iterations):
            new_pr = {cid: (1.0 - d) / n for cid in concept_ids}
            # Handle dangling nodes (nodes with out-degree = 0)
            dangling_sum = sum(pagerank[cid] for cid in concept_ids if not adj_out[cid])
            dangling_contrib = d * dangling_sum / n
            
            for cid in concept_ids:
                new_pr[cid] += dangling_contrib

                # Transmit PageRank from incoming nodes
                for neighbor in adj_in[cid]:
                    out_deg = len(adj_out[neighbor])
                    if out_deg > 0:
                        new_pr[cid] += d * pagerank[neighbor] / out_deg

            pagerank = new_pr

        # 4. Betweenness Centrality (BFS shortest paths count)
        betweenness = {cid: 0.0 for cid in concept_ids}
        for s in concept_ids:
            # Stack of visited nodes in BFS order
            S = []
            # List of predecessors on shortest paths from s
            P: Dict[uuid.UUID, List[uuid.UUID]] = {cid: [] for cid in concept_ids}
            # Number of shortest paths from s to v
            sigma = {cid: 0 for cid in concept_ids}
            sigma[s] = 1
            # Distance from s to v
            d_dist = {cid: -1 for cid in concept_ids}
            d_dist[s] = 0

            queue = [s]
            while queue:
                v = queue.pop(0)
                S.append(v)
                for w in adj_out[v]:
                    # Path discovery
                    if d_dist[w] < 0:
                        d_dist[w] = d_dist[v] + 1
                        queue.append(w)
                    # Path counting
                    if d_dist[w] == d_dist[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)

            # Accumulate dependency delta
            delta = {cid: 0.0 for cid in concept_ids}
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        # Normalize betweenness (divide by (n-1)*(n-2) if n > 2)
        norm_factor = (n - 1) * (n - 2) if n > 2 else 1.0
        for cid in concept_ids:
            betweenness[cid] /= norm_factor

        # 5. Impact Score Calculation
        # Quantify downstream cascade size if concept v changes
        impact_scores: Dict[uuid.UUID, float] = {}
        for cid in concept_ids:
            # Transitively find all dependent concepts (BFS backwards on incoming edges)
            visited: Set[uuid.UUID] = set()
            queue = [(cid, 1.0)] # tuple of (node, path_confidence)
            visited.add(cid)
            impact = 0.0

            while queue:
                curr, path_conf = queue.pop(0)
                if curr != cid:
                    entity_cnt = concept_sizes.get(curr, (0, 0))[0]
                    impact += path_conf * entity_cnt

                for neighbor in adj_out[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        link_conf = edge_confidences.get((curr, neighbor), 1.0)
                        queue.append((neighbor, path_conf * link_conf))

            impact_scores[cid] = impact

        # 6. Build ConceptMetrics entities
        namespace = uuid.UUID("f1a08555-de7b-49fa-98e6-d9b2cafac234")
        metrics_list = []
        for c_node, c_ver, _ in detected_concepts:
            cid = c_node.id
            ent_cnt, file_cnt = concept_sizes.get(cid, (0, 0))
            in_deg = len(adj_in[cid])
            out_deg = len(adj_out[cid])

            # Normalized degree centrality
            deg_centrality = (in_deg + out_deg) / (n - 1) if n > 1 else 0.0

            metrics_id = uuid.uuid5(namespace, f"metrics:{c_ver.id}")
            metrics_list.append(
                ConceptMetrics(
                    id=metrics_id,
                    concept_version_id=c_ver.id,
                    entity_count=ent_cnt,
                    file_count=file_cnt,
                    in_degree=in_deg,
                    out_degree=out_deg,
                    degree_centrality=deg_centrality,
                    betweenness_centrality=betweenness[cid],
                    pagerank_score=pagerank[cid],
                    impact_score=impact_scores[cid],
                    computed_at=datetime.utcnow(),
                )
            )

        return metrics_list
