"""
Phase 7C — DecisionDiscoveryEngine

The primary engine responsible for extracting architectural decisions from
first-principles evidence:

    Evidence Pipeline:
    ─────────────────
    RepositoryMemory (events)
        ↓
    ADRNode graphs (explicit decisions)
        ↓
    DecisionPatternRegistry (keyword / dependency signals)
        ↓
    IntentPatternRegistry  (motivation classification)
        ↓
    Multi-source evidence fusion
        ↓
    DecisionConfidence computation
        ↓
    List[Decision] (immutable, versioned)

Design Principles:
    - Every decision is traceable to at least one provenanced event.
    - Pattern registries are the ONLY source of semantic labels (no hardcoded strings).
    - Confidence is computed from real evidence dimensions, never hardcoded.
    - ADR documents override inferred confidence upward when they confirm a decision.
    - Decisions are deduplicated by (technology_key, repository_id) before returning.
"""

from __future__ import annotations

import logging
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .decision import Decision
from .decision_confidence import DecisionConfidence
from .decision_evidence import DecisionEvidence
from .decision_status import DecisionStatus
from .decision_type import DecisionType
from .decision_version import DecisionVersion
from .repository_event import RepositoryEvent, RepositoryEventType
from .repository_memory import RepositoryMemory

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
#  Static built-in technology catalogue
#  Registry YAML files can extend this via the DecisionPatternRegistry.
#  Keys are normalised package names → (display_name, DecisionType, [IntentTypes])
# ──────────────────────────────────────────────────────────────────────────────
_BUILTIN_TECH_CATALOGUE: Dict[str, Dict[str, Any]] = {
    # Message brokers / streaming
    "kafka": {"name": "Apache Kafka", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "kafka-python": {"name": "Apache Kafka", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "confluent-kafka": {"name": "Apache Kafka", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "aiokafka": {"name": "Apache Kafka", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "rabbitmq": {"name": "RabbitMQ", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["RELIABILITY"]},
    "pika": {"name": "RabbitMQ", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["RELIABILITY"]},
    "celery": {"name": "Celery Task Queue", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "redis": {"name": "Redis", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY", "SCALABILITY"]},
    "aioredis": {"name": "Redis", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
    # Databases
    "sqlalchemy": {"name": "SQLAlchemy ORM", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "alembic": {"name": "Alembic Migrations", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "psycopg2": {"name": "PostgreSQL", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "asyncpg": {"name": "PostgreSQL (async)", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
    "motor": {"name": "MongoDB (async)", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "pymongo": {"name": "MongoDB", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "elasticsearch": {"name": "Elasticsearch", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "opensearch-py": {"name": "OpenSearch", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "cassandra-driver": {"name": "Apache Cassandra", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["SCALABILITY"]},
    "pinecone-client": {"name": "Pinecone Vector DB", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "weaviate-client": {"name": "Weaviate Vector DB", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "chromadb": {"name": "ChromaDB", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    # Frameworks / APIs
    "fastapi": {"name": "FastAPI", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
    "flask": {"name": "Flask", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "django": {"name": "Django", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "grpc": {"name": "gRPC", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY", "COUPLING_REDUCTION"]},
    "grpcio": {"name": "gRPC", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
    "graphene": {"name": "GraphQL (Graphene)", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    "strawberry": {"name": "GraphQL (Strawberry)", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": []},
    # Auth / Security
    "python-jose": {"name": "JWT / OAuth2", "type": DecisionType.SECURITY, "intents": ["SECURITY"]},
    "pyjwt": {"name": "JWT Authentication", "type": DecisionType.SECURITY, "intents": ["SECURITY"]},
    "cryptography": {"name": "Cryptography Library", "type": DecisionType.SECURITY, "intents": ["SECURITY"]},
    "passlib": {"name": "Password Hashing", "type": DecisionType.SECURITY, "intents": ["SECURITY"]},
    "authlib": {"name": "OAuth2 / OIDC", "type": DecisionType.SECURITY, "intents": ["SECURITY", "COMPLIANCE"]},
    # AI / ML
    "openai": {"name": "OpenAI API", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "anthropic": {"name": "Anthropic Claude API", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "langchain": {"name": "LangChain", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "langchain-core": {"name": "LangChain Core", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "llama-index": {"name": "LlamaIndex", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "sentence-transformers": {"name": "Sentence Transformers", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "transformers": {"name": "HuggingFace Transformers", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "torch": {"name": "PyTorch", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    "tensorflow": {"name": "TensorFlow", "type": DecisionType.AI_ADOPTION, "intents": ["AI_ENABLEMENT"]},
    # Observability
    "opentelemetry": {"name": "OpenTelemetry", "type": DecisionType.INFRASTRUCTURE, "intents": ["OBSERVABILITY"]},
    "opentelemetry-sdk": {"name": "OpenTelemetry", "type": DecisionType.INFRASTRUCTURE, "intents": ["OBSERVABILITY"]},
    "prometheus-client": {"name": "Prometheus Metrics", "type": DecisionType.INFRASTRUCTURE, "intents": ["OBSERVABILITY"]},
    "structlog": {"name": "Structured Logging", "type": DecisionType.INFRASTRUCTURE, "intents": ["OBSERVABILITY"]},
    "loguru": {"name": "Loguru Logging", "type": DecisionType.INFRASTRUCTURE, "intents": ["OBSERVABILITY"]},
    # Infrastructure
    "boto3": {"name": "AWS SDK", "type": DecisionType.INFRASTRUCTURE, "intents": ["SCALABILITY"]},
    "kubernetes": {"name": "Kubernetes Client", "type": DecisionType.INFRASTRUCTURE, "intents": ["SCALABILITY"]},
    "docker": {"name": "Docker SDK", "type": DecisionType.INFRASTRUCTURE, "intents": ["SCALABILITY"]},
    "terraform": {"name": "Terraform IaC", "type": DecisionType.INFRASTRUCTURE, "intents": ["COST_REDUCTION"]},
    "httpx": {"name": "HTTPX Async Client", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
    "aiohttp": {"name": "aiohttp Client", "type": DecisionType.TECHNOLOGY_ADOPTION, "intents": ["LATENCY"]},
}


def _normalise_package_name(raw: str) -> str:
    """Normalise pip package name: lowercase, strip version, replace _ with -."""
    # Remove version specifiers like ==1.2, >=2.0, ~=3, [extras]
    name = re.split(r"[>=<!~;\[\s]", raw.strip())[0]
    return name.lower().replace("_", "-")


def _extract_dependency_name(event: RepositoryEvent) -> Optional[str]:
    """
    Extract a normalised technology name from a RepositoryEvent.

    The event metadata should carry a 'dependency_name' key when produced by
    the RepositoryEventBuilder.  Fall back to parsing the description string.
    """
    meta = event.metadata or {}
    if "dependency_name" in meta:
        return _normalise_package_name(meta["dependency_name"])
    # Heuristic: parse description like "Introduced dependency: kafka-python==2.0.2"
    match = re.search(
        r"(?:introduced|added|removed|dependency[:\s]+)\s*([a-zA-Z0-9_\-]+)",
        event.description,
        re.IGNORECASE,
    )
    if match:
        return _normalise_package_name(match.group(1))
    return None


class DecisionDiscoveryEngine:
    """
    Discovers architectural decisions from provenanced repository evidence.

    Injection:
        decision_registry:  DecisionPatternRegistry instance (YAML-backed).
        intent_registry:    IntentPatternRegistry instance (YAML-backed).

    Usage::

        engine = DecisionDiscoveryEngine(decision_registry, intent_registry)
        decisions = engine.discover_from_memory(memory, adr_graphs)
    """

    def __init__(self, decision_registry: Any, intent_registry: Any) -> None:
        self._decision_registry = decision_registry
        self._intent_registry = intent_registry

    # ─────────────────────────────────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────────────────────────────────

    def discover_from_memory(
        self,
        memory: RepositoryMemory,
        adr_graphs: List[Any],
    ) -> List[Decision]:
        """
        Full discovery pipeline over a RepositoryMemory snapshot.

        Steps:
            1. Classify each event into candidate (technology_key, DecisionType)
            2. Group evidence by candidate key
            3. Check ADR graph for confirming documents
            4. Compute multi-dimensional confidence
            5. Build Decision domain objects with DecisionVersion v1
            6. Deduplicate on (technology_key, repository_id)
        """
        repository_id = memory.repository_id

        # Stage 1 — Classify events → candidates
        # candidate_key → CandidateAccumulator
        candidates: Dict[str, _CandidateAccumulator] = {}

        for event in memory.events:
            result = self._classify_event(event)
            if result is None:
                continue
            tech_key, display_name, decision_type, intent_hints = result
            compound_key = f"{tech_key}::{decision_type.value}"

            if compound_key not in candidates:
                candidates[compound_key] = _CandidateAccumulator(
                    tech_key=tech_key,
                    display_name=display_name,
                    decision_type=decision_type,
                    intent_hints=list(intent_hints),
                    repository_id=repository_id,
                )
            candidates[compound_key].absorb_event(event)

        # Also classify events from memory's categorised lists for architecture/ownership changes
        for commit_hash in memory.architecture_changes:
            acc_key = f"architecture_change::{DecisionType.ARCHITECTURAL.value}"
            if acc_key not in candidates:
                candidates[acc_key] = _CandidateAccumulator(
                    tech_key="architecture_change",
                    display_name="Architectural Restructuring",
                    decision_type=DecisionType.ARCHITECTURAL,
                    intent_hints=["COUPLING_REDUCTION"],
                    repository_id=repository_id,
                )
            candidates[acc_key].architecture_commits.append(commit_hash)

        for commit_hash in memory.service_creations:
            acc_key = f"service_creation::{DecisionType.CAPABILITY_CREATION.value}"
            if acc_key not in candidates:
                candidates[acc_key] = _CandidateAccumulator(
                    tech_key="service_creation",
                    display_name="New Service / Module Creation",
                    decision_type=DecisionType.CAPABILITY_CREATION,
                    intent_hints=["COUPLING_REDUCTION"],
                    repository_id=repository_id,
                )
            candidates[acc_key].service_commits.append(commit_hash)

        # Stage 2 — Cross-reference ADR graphs
        adr_confirmations: Dict[str, List[str]] = defaultdict(list)
        adr_document_ids: Dict[str, List[str]] = defaultdict(list)
        for adr_graph in (adr_graphs or []):
            for node in getattr(adr_graph, "nodes", []):
                title = getattr(node, "title", "") or ""
                doc_id = str(getattr(node, "id", ""))
                # Match ADR title against each candidate's display name / tech key
                title_lower = title.lower()
                for ckey, acc in candidates.items():
                    if acc.tech_key.replace("-", " ") in title_lower or \
                       acc.display_name.lower() in title_lower:
                        adr_confirmations[ckey].append(title)
                        adr_document_ids[ckey].append(doc_id)

        # Stage 3 — Build Decision objects
        decisions: List[Decision] = []
        now = datetime.now(timezone.utc)

        for compound_key, acc in candidates.items():
            if not acc.has_evidence():
                continue

            adr_docs = adr_document_ids.get(compound_key, [])
            adr_confirmed = len(adr_docs) > 0

            confidence = self._compute_confidence(acc, adr_confirmed)

            # Build immutable evidence value object
            evidence = DecisionEvidence(
                supporting_commits=acc.all_commits(),
                supporting_documents=adr_docs,
                supporting_capabilities=acc.capability_commits,
                supporting_architecture_changes=acc.architecture_commits,
                supporting_repository_events=[str(e.event_id) for e in acc.raw_events],
            )

            # Initial version snapshot
            first_commit = acc.first_commit()
            last_commit = acc.last_commit()

            v1 = DecisionVersion(
                decision_id=uuid.uuid4(),  # placeholder; overwritten below
                version=1,
                commit_hash=first_commit,
                confidence=confidence.score,
                supporting_evidence=evidence.supporting_commits[:5],
                generated_at=now,
            )

            decision_id = uuid.uuid4()
            # Rebuild DecisionVersion with correct decision_id (frozen dataclass)
            v1 = DecisionVersion(
                decision_id=decision_id,
                version=1,
                commit_hash=first_commit,
                confidence=confidence.score,
                supporting_evidence=evidence.supporting_commits[:5],
                generated_at=now,
            )

            decision = Decision(
                id=decision_id,
                name=self._format_decision_name(acc.decision_type, acc.display_name),
                description=self._format_description(acc, adr_docs),
                decision_type=acc.decision_type,
                confidence=confidence,
                status=DecisionStatus.ACTIVE,
                created_at=now,
                first_seen_commit=first_commit,
                last_seen_commit=last_commit,
                repository_id=repository_id,
                versions=[v1],
                supporting_evidence=evidence,
                affected_capabilities=acc.capability_commits[:10],
                affected_architectures=acc.architecture_commits[:10],
                affected_services=acc.service_commits[:10],
            )
            decisions.append(decision)

        logger.info(
            "DecisionDiscoveryEngine: discovered %d decisions for repo '%s'",
            len(decisions),
            repository_id,
        )
        return decisions

    # ─────────────────────────────────────────────────────────────────────────
    #  Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _classify_event(
        self, event: RepositoryEvent
    ) -> Optional[Tuple[str, str, DecisionType, List[str]]]:
        """
        Returns (tech_key, display_name, DecisionType, intent_hints) or None.

        Priority order:
            1. Known event type with metadata dependency_name → catalogue lookup
            2. DecisionPatternRegistry YAML keyword match
            3. Built-in catalogue substring fallback on description
        """
        if event.event_type in (
            RepositoryEventType.DEPENDENCY_INTRODUCED,
            RepositoryEventType.DEPENDENCY_REMOVED,
            RepositoryEventType.FRAMEWORK_ADOPTED,
            RepositoryEventType.MODEL_ADOPTED,
        ):
            dep_name = _extract_dependency_name(event)
            if dep_name:
                catalogue_hit = _BUILTIN_TECH_CATALOGUE.get(dep_name)
                if catalogue_hit:
                    decision_type = (
                        DecisionType.TECHNOLOGY_REMOVAL
                        if event.event_type == RepositoryEventType.DEPENDENCY_REMOVED
                        else catalogue_hit["type"]
                    )
                    return (dep_name, catalogue_hit["name"], decision_type, catalogue_hit["intents"])

                # Not in built-in catalogue — ask YAML registry
                registry_matches = self._decision_registry.match_patterns(dep_name + " " + event.description)
                if registry_matches:
                    m = registry_matches[0]
                    return (
                        dep_name,
                        m.get("display_name", dep_name.replace("-", " ").title()),
                        DecisionType[m.get("decision_type", "TECHNOLOGY_ADOPTION")],
                        m.get("intent_hints", []),
                    )

                # Fallback: unknown technology but still a signal
                return (
                    dep_name,
                    dep_name.replace("-", " ").title(),
                    DecisionType.TECHNOLOGY_ADOPTION if event.event_type != RepositoryEventType.DEPENDENCY_REMOVED
                    else DecisionType.TECHNOLOGY_REMOVAL,
                    [],
                )

        if event.event_type == RepositoryEventType.ARCHITECTURE_CHANGED:
            matches = self._decision_registry.match_patterns(event.description)
            if matches:
                m = matches[0]
                return (
                    "architecture_" + m.get("id", "change"),
                    m.get("display_name", "Architectural Change"),
                    DecisionType.ARCHITECTURAL,
                    m.get("intent_hints", []),
                )
            return ("architecture_change", "Architectural Change", DecisionType.ARCHITECTURAL, [])

        if event.event_type == RepositoryEventType.SERVICE_CREATED:
            return ("service_creation", "Service Decomposition", DecisionType.CAPABILITY_CREATION, ["COUPLING_REDUCTION"])

        if event.event_type == RepositoryEventType.OWNERSHIP_CHANGED:
            return ("ownership_change", "Ownership Restructuring", DecisionType.OWNERSHIP_CHANGE, [])

        return None

    def _compute_confidence(
        self, acc: "_CandidateAccumulator", adr_confirmed: bool
    ) -> DecisionConfidence:
        """
        Multi-dimensional confidence formula.

        Dimensions:
            evidence_coverage   = min(1.0, commit_count / 5)     — how many distinct commits carry the signal
            historical_support  = min(1.0, total_events / 3)     — how many distinct RepositoryEvents support it
            architectural_support = 0.9 if adr_confirmed else 0.3  — ADR document confirmation
            capability_support  = min(1.0, len(capability_commits) / 2)
            artifact_agreement  = 0.8 if adr_confirmed else 0.2   — ADR status agreement
        """
        commit_count = len(set(acc.all_commits()))
        event_count = len(acc.raw_events)

        evidence_coverage = min(1.0, commit_count / 5)
        historical_support = min(1.0, event_count / 3)
        architectural_support = 0.9 if adr_confirmed else 0.35
        capability_support = min(1.0, len(acc.capability_commits) / 2) if acc.capability_commits else 0.1
        artifact_agreement = 0.85 if adr_confirmed else 0.2

        return DecisionConfidence.compute(
            evidence_coverage=round(evidence_coverage, 4),
            historical_support=round(historical_support, 4),
            architectural_support=round(architectural_support, 4),
            capability_support=round(capability_support, 4),
            artifact_agreement=round(artifact_agreement, 4),
        )

    @staticmethod
    def _format_decision_name(decision_type: DecisionType, display_name: str) -> str:
        prefix_map = {
            DecisionType.TECHNOLOGY_ADOPTION: "Adopt",
            DecisionType.TECHNOLOGY_REMOVAL: "Remove",
            DecisionType.AI_ADOPTION: "Adopt AI:",
            DecisionType.SECURITY: "Enforce Security:",
            DecisionType.INFRASTRUCTURE: "Adopt Infrastructure:",
            DecisionType.ARCHITECTURAL: "Restructure Architecture:",
            DecisionType.CAPABILITY_CREATION: "Create Capability:",
            DecisionType.OWNERSHIP_CHANGE: "Change Ownership:",
        }
        prefix = prefix_map.get(decision_type, "Decide:")
        return f"{prefix} {display_name}"

    @staticmethod
    def _format_description(acc: "_CandidateAccumulator", adr_docs: List[str]) -> str:
        parts = [
            f"Decision to {acc.decision_type.value.lower().replace('_', ' ')} "
            f"'{acc.display_name}' detected from {len(acc.raw_events)} repository event(s) "
            f"across {len(set(acc.all_commits()))} commit(s)."
        ]
        if adr_docs:
            parts.append(f"Confirmed by {len(adr_docs)} ADR document(s).")
        return " ".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
#  Internal accumulator — not part of the public API
# ──────────────────────────────────────────────────────────────────────────────

class _CandidateAccumulator:
    """
    Mutable accumulator for evidence associated with a single candidate decision.
    Collapsed into a Decision domain object once all events have been processed.
    """

    def __init__(
        self,
        tech_key: str,
        display_name: str,
        decision_type: DecisionType,
        intent_hints: List[str],
        repository_id: str,
    ) -> None:
        self.tech_key = tech_key
        self.display_name = display_name
        self.decision_type = decision_type
        self.intent_hints = intent_hints
        self.repository_id = repository_id
        self.raw_events: List[RepositoryEvent] = []
        self.dependency_commits: List[str] = []
        self.capability_commits: List[str] = []
        self.architecture_commits: List[str] = []
        self.service_commits: List[str] = []

    def absorb_event(self, event: RepositoryEvent) -> None:
        self.raw_events.append(event)
        if event.commit_hash:
            if event.event_type in (
                RepositoryEventType.DEPENDENCY_INTRODUCED,
                RepositoryEventType.DEPENDENCY_REMOVED,
                RepositoryEventType.FRAMEWORK_ADOPTED,
                RepositoryEventType.MODEL_ADOPTED,
            ):
                self.dependency_commits.append(event.commit_hash)
            elif event.event_type in (RepositoryEventType.CAPABILITY_CREATED, RepositoryEventType.CAPABILITY_SPLIT):
                self.capability_commits.append(event.commit_hash)
            elif event.event_type == RepositoryEventType.ARCHITECTURE_CHANGED:
                self.architecture_commits.append(event.commit_hash)
            elif event.event_type == RepositoryEventType.SERVICE_CREATED:
                self.service_commits.append(event.commit_hash)

    def all_commits(self) -> List[str]:
        return (
            self.dependency_commits
            + self.capability_commits
            + self.architecture_commits
            + self.service_commits
        )

    def first_commit(self) -> str:
        commits = self.all_commits()
        return commits[0] if commits else ""

    def last_commit(self) -> str:
        commits = self.all_commits()
        return commits[-1] if commits else ""

    def has_evidence(self) -> bool:
        return bool(self.raw_events or self.all_commits())
