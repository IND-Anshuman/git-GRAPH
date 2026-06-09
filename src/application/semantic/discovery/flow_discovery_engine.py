"""Flow Discovery Engine to trace and categorize multi-hop execution flow sequences."""

import uuid
from typing import Any, Dict, List, Set, Tuple
from src.application.ports.unit_of_work import IUnitOfWork
from src.application.semantic.isr.canonical_flow import CanonicalFlow
from src.domain.value_objects.flow_evidence import FlowEvidence
from src.domain.value_objects.flow_fingerprint import FlowFingerprint
from src.domain.entities.microservice_boundary import MicroserviceBoundary
from src.domain.enums.relationship_type import RelationshipType
from src.domain.value_objects.repository_id import RepositoryId


class FlowDiscoveryEngine:
    """Discovers and categorizes execution paths, distributed boundaries, and AI agent workflows."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def discover_flows(self, repository_id: RepositoryId) -> List[CanonicalFlow]:
        """Queries the entity graph, traces multi-hop chains, and returns list of CanonicalFlow objects."""
        flows: List[CanonicalFlow] = []

        with self.uow:
            # 1. Fetch entities and relationships
            db_entities = self.uow.code_entities.get_by_repository(repository_id)
            if not db_entities:
                return []

            entity_map = {str(e.seid.value): e for e in db_entities}
            relationships = self.uow.relationships.get_by_repository(repository_id)

            # Build adjacency list: node_id -> list of (target_node_id, relationship_type, rel_id)
            adj: Dict[str, List[Tuple[str, str, str]]] = {}
            for r in relationships:
                src = str(r.source_seid.value)
                tgt = str(r.target_seid.value)
                rel_type = r.relationship_type.name if hasattr(r.relationship_type, "name") else str(r.relationship_type)
                
                if src not in adj:
                    adj[src] = []
                adj[src].append((tgt, rel_type, str(r.id)))

            # 2. Trace execution paths using DFS
            visited: Set[str] = set()

            for start_id in entity_map:
                path = [start_id]
                self._trace_paths_dfs(start_id, path, adj, entity_map, visited, flows)

        return flows

    def _trace_paths_dfs(
        self,
        curr_id: str,
        path: List[str],
        adj: Dict[str, List[Tuple[str, str, str]]],
        entity_map: Dict[str, Any],
        visited: Set[str],
        flows: List[CanonicalFlow],
    ) -> None:
        # Avoid extremely long or cyclical flows
        if len(path) > 7:
            self._save_discovered_flow(path, adj, entity_map, flows)
            return

        # If leaf node (no outbound edges), save the flow
        targets = adj.get(curr_id, [])
        if not targets:
            if len(path) >= 2:
                self._save_discovered_flow(path, adj, entity_map, flows)
            return

        for tgt, rel_type, rel_id in targets:
            if tgt not in path:  # Simple cycle prevention
                path.append(tgt)
                self._trace_paths_dfs(tgt, path, adj, entity_map, visited, flows)
                path.pop()

    def _save_discovered_flow(
        self,
        path: List[str],
        adj: Dict[str, List[Tuple[str, str, str]]],
        entity_map: Dict[str, Any],
        flows: List[CanonicalFlow],
    ) -> None:
        source_id = path[0]
        target_id = path[-1]
        intermediates = path[1:-1]

        source_entity = entity_map.get(source_id)
        target_entity = entity_map.get(target_id)
        if not source_entity or not target_entity:
            return

        # 1. Determine Flow Type
        flow_type = self._determine_flow_type(path, entity_map)

        # 2. Extract Traversed Relationships and microservice boundaries
        rel_ids: List[str] = []
        boundary_count = 0
        node_types: List[str] = []

        for i in range(len(path) - 1):
            src = path[i]
            tgt = path[i + 1]
            ent = entity_map.get(src)
            if ent:
                t = ent.metadata.get("entity_type")
                if not t:
                    t = ent.entity_type.value if hasattr(ent.entity_type, "value") else str(ent.entity_type)
                node_types.append(t)

            # Match relationship
            for next_tgt, r_type, r_id in adj.get(src, []):
                if next_tgt == tgt:
                    rel_ids.append(r_id)
                    if r_type in ("CALLS_ENDPOINT", "PUBLISHES_TO_TOPIC", "CONSUMES_FROM_TOPIC"):
                        boundary_count += 1
                    break

        last_ent = entity_map.get(target_id)
        if last_ent:
            t = last_ent.metadata.get("entity_type")
            if not t:
                t = last_ent.entity_type.value if hasattr(last_ent.entity_type, "value") else str(last_ent.entity_type)
            node_types.append(t)

        # 3. Create FlowEvidence and FlowFingerprint
        evidence = FlowEvidence(
            entities=path,
            relationships=rel_ids,
            behaviors=[],  # logic evidence would be populated if behaviors matched
            confidence_breakdown={"structural_depth": float(len(path)) / 7.0},
        )

        calls_signature = ", ".join(entity_map[nid].name for nid in path)
        fingerprint = FlowFingerprint(
            node_sequence=node_types,
            hop_count=len(path) - 1,
            boundary_count=boundary_count,
            calls_signature=calls_signature,
        )

        flow_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"flow:{source_id}:{target_id}:" + "-".join(intermediates)))

        # Build metadata
        metadata = {
            "evidence": evidence.to_dict(),
            "fingerprint": fingerprint.to_dict(),
            "source_name": source_entity.name,
            "target_name": target_entity.name,
        }

        canonical_flow = CanonicalFlow(
            id=flow_id,
            flow_type=flow_type,
            source_entity_id=source_id,
            target_entity_id=target_id,
            intermediate_entities=intermediates,
            confidence=0.90,
            metadata=metadata,
        )
        flows.append(canonical_flow)

    def _determine_flow_type(self, path: List[str], entity_map: Dict[str, Any]) -> str:
        """Determines flow type category based on entity types in the sequence."""
        types = []
        for nid in path:
            ent = entity_map[nid]
            t = ent.metadata.get("entity_type")
            if not t:
                t = ent.entity_type.value if hasattr(ent.entity_type, "value") else str(ent.entity_type)
            types.append(t)

        # 1. AI agent workflow
        # Check: Agent, Model, Tool, Memory, Planner, Router, Evaluator, Guardrail, Reflection Loop
        ai_types = {"Agent", "Model", "Tool", "Memory", "Planner", "Router", "Evaluator", "Guardrail", "ReflectionLoop"}
        if any(t in ai_types for t in types):
            return "AI Flow"

        # 2. Frontend user flow
        frontend_types = {"Component", "Hook", "Store", "Page"}
        if any(t in frontend_types for t in types):
            return "Frontend Flow"

        # 3. Messaging flow
        messaging_types = {"Producer", "Consumer", "Topic", "ConsumerGroup"}
        if any(t in messaging_types for t in types):
            return "Messaging Flow"

        # Default fallback
        return "Execution Flow"
