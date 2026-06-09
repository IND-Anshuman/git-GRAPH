"""Relationship Discovery Engine service to dynamically discover semantic interaction edges."""

import uuid
from typing import Any, Dict, List, Tuple
from src.application.ports.unit_of_work import IUnitOfWork
from src.domain.entities.relationship import Relationship
from src.domain.enums.relationship_type import RelationshipType
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.relationship_evidence import RelationshipEvidence
from src.application.semantic.isr.canonical_entity import CanonicalEntity
from src.application.semantic.isr.canonical_behavior import CanonicalBehavior
from src.application.semantic.isr.canonical_flow import CanonicalFlow
from src.application.semantic.calibration.calibration_engine import ConfidenceCalibrationEngine
from src.application.semantic.discovery.route_normalizer import RouteNormalizer


class RelationshipDiscoveryEngine:
    """Discovers structural, behavioral, distributed, frontend, and AI relationships from ISR."""

    def __init__(self, uow: IUnitOfWork, calibration_engine: ConfidenceCalibrationEngine):
        self.uow = uow
        self.calibration_engine = calibration_engine

    def discover_relationships(
        self,
        repository_id: RepositoryId,
        entities: List[CanonicalEntity],
        behaviors: List[CanonicalBehavior],
        flows: List[CanonicalFlow],
    ) -> List[Relationship]:
        """Scans Intermediate Semantic Representation elements and discovers dynamic coupling edges."""
        discovered_relationships: List[Relationship] = []
        entity_map = {e.id: e for e in entities}

        # 1. Tracing flows to extract execution and data flow links
        for flow in flows:
            path = [flow.source_entity_id] + flow.intermediate_entities + [flow.target_entity_id]
            for i in range(len(path) - 1):
                source_id = path[i]
                target_id = path[i + 1]

                source_entity = entity_map.get(source_id)
                target_entity = entity_map.get(target_id)

                if not source_entity or not target_entity:
                    continue

                rel_type, evidence = self._infer_relationship_type(
                    source_entity, target_entity, flow
                )
                
                # Calibrate confidence using flow confidence and baseline parameters
                calibrated_conf = self.calibration_engine.calibrate_joint_confidence(
                    evidence_scores=[flow.confidence, 0.85],
                    max_single_score=flow.confidence,
                )

                relationship = Relationship(
                    id=uuid.uuid4(),
                    repository_id=repository_id,
                    relationship_type=rel_type,
                    source_seid=SEID.from_string(source_entity.id)
                    if self._is_valid_uuid(source_entity.id)
                    else SEID.generate(),
                    target_seid=SEID.from_string(target_entity.id)
                    if self._is_valid_uuid(target_entity.id)
                    else SEID.generate(),
                    confidence=calibrated_conf,
                    metadata={
                        "evidence": evidence.to_dict(),
                        "flow_origin_id": flow.id,
                        "source_name": source_entity.name,
                        "target_name": target_entity.name,
                    },
                )
                discovered_relationships.append(relationship)

        # 2. Match Client-Server RPC paths dynamically using RouteNormalizer
        clients = [e for e in entities if e.entity_type in ("APIClient", "Client", "Component")]
        endpoints = [e for e in entities if e.entity_type in ("APIEndpoint", "Controller", "Route")]
        for client in clients:
            client_routes = client.metadata.get("routes", [])
            if client.metadata.get("http_route"):
                client_routes.append(client.metadata.get("http_route"))
            
            for endpoint in endpoints:
                server_route = endpoint.metadata.get("http_route") or endpoint.metadata.get("route")
                if not server_route:
                    continue
                
                for client_route in client_routes:
                    if RouteNormalizer.match_routes(client_route, server_route):
                        evidence = RelationshipEvidence(
                            matched_routes=[client_route, server_route],
                            matched_calls=[f"{client.name} calls route {server_route}"],
                            matched_types=[client.entity_type, endpoint.entity_type],
                        )
                        
                        relationship = Relationship(
                            id=uuid.uuid4(),
                            repository_id=repository_id,
                            relationship_type=RelationshipType.CALLS_ENDPOINT,
                            source_seid=SEID.from_string(client.id)
                            if self._is_valid_uuid(client.id)
                            else SEID.generate(),
                            target_seid=SEID.from_string(endpoint.id)
                            if self._is_valid_uuid(endpoint.id)
                            else SEID.generate(),
                            confidence=0.90,
                            metadata={
                                "evidence": evidence.to_dict(),
                                "client_route": client_route,
                                "server_route": server_route,
                                "source_name": client.name,
                                "target_name": endpoint.name,
                            },
                        )
                        discovered_relationships.append(relationship)

        # Save to database
        with self.uow:
            for rel in discovered_relationships:
                self.uow.relationships.save(rel)
            self.uow.commit()

        return discovered_relationships

    def _infer_relationship_type(
        self,
        source: CanonicalEntity,
        target: CanonicalEntity,
        flow: CanonicalFlow,
    ) -> Tuple[RelationshipType, RelationshipEvidence]:
        """Infers RelationshipType and produces structured evidence based on entities in a flow context."""
        s_type = source.entity_type
        t_type = target.entity_type

        evidence = RelationshipEvidence(
            matched_types=[s_type, t_type],
            matched_dataflows=[f"Flow {flow.id} traverses {source.name} -> {target.name}"],
        )

        # 1. AI-Native Relationships
        if s_type == "Agent":
            if t_type == "Model":
                return RelationshipType.CALLS_MODEL, evidence
            elif t_type == "Tool":
                return RelationshipType.USES_TOOL, evidence
            elif t_type == "Agent":
                return RelationshipType.ROUTES_TO_AGENT, evidence
            elif t_type in ("VectorDB", "Retriever"):
                return RelationshipType.RETRIEVES_CONTEXT, evidence
            elif t_type in ("Memory", "Store"):
                # Check if it is a write flow or read flow
                if "write" in flow.flow_type.lower() or "save" in flow.flow_type.lower():
                    return RelationshipType.WRITES_MEMORY, evidence
                return RelationshipType.READS_MEMORY, evidence
            elif t_type == "Evaluator":
                return RelationshipType.EVALUATES_OUTPUT, evidence
            elif t_type == "ReflectionLoop":
                return RelationshipType.REFLECTS_ON_RESULT, evidence

        # 2. Messaging / Queue Relationships
        if s_type == "Producer":
            if t_type == "Topic":
                return RelationshipType.PUBLISHES_TO_TOPIC, evidence
        elif s_type == "Consumer":
            if t_type == "Topic":
                return RelationshipType.CONSUMES_FROM_TOPIC, evidence
            elif t_type == "ConsumerGroup":
                return RelationshipType.BELONGS_TO_GROUP, evidence

        # 3. Frontend UI Relationships
        if s_type == "Component":
            if t_type == "Hook":
                return RelationshipType.USES_HOOK, evidence
            elif t_type == "Store":
                return RelationshipType.DISPATCHES_ACTION, evidence
        elif s_type == "Page":
            if t_type == "Page":
                return RelationshipType.NAVIGATES_TO, evidence

        # 4. Standard Backend / RPC Fallbacks
        if s_type in ("APIClient", "Client") and t_type in ("APIEndpoint", "Controller"):
            return RelationshipType.CALLS_ENDPOINT, evidence
        if s_type == "Controller" and t_type == "Service":
            return RelationshipType.PASSES_STATE_TO, evidence
        if s_type == "Service" and t_type == "Repository":
            return RelationshipType.INJECTED_INTO, evidence

        # Global Fallbacks
        return RelationshipType.PASSES_STATE_TO, evidence

    @staticmethod
    def _is_valid_uuid(val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
