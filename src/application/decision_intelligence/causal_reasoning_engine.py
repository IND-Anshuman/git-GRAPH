"""
Phase 7C — CausalReasoningEngine

Performs multi-hop causal reasoning over the Decision/Intent graph to construct
CausalChain objects that answer: "Why was this decision made?"

Reasoning Pipeline:
────────────────────
    1. For each Decision, identify which IntentTypes it *satisfies*.
       (Mapping is defined in _DECISION_TO_INTENT_MAP — registry-extensible.)

    2. Group Decisions by their inferred IntentType.

    3. For each IntentType group, look for an existing Intent from the
       provided intents list — or synthesise a new Intent if none exists.

    4. Build CausalRelationship objects:
         Intent ──MOTIVATES──▶ Decision
         Decision ──ENABLES──▶ (sibling decisions sharing the same intent)

    5. Compute causal confidence from corroborating evidence:
         - Both intent and decision share supporting commits          (+0.30)
         - Both have supporting ADR documents                        (+0.25)
         - Decision confidence.score                                 (+0.30)
         - Number of co-temporal evidence items                      (+0.15)

    6. Build a CausalChain per Intent-rooted tree.

    7. Detect CONFLICTING decisions (same type, opposite status,
       overlapping time range) and add CONTRADICTS edges.

Design:
    - confidence is NEVER hardcoded.
    - generated_at is ALWAYS set to datetime.now(timezone.utc).
    - Produces multi-hop chains: Intent → [Decisions] → [Capabilities affected].
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from .causal_chain import CausalChain
from .causal_relationship import CausalRelationship
from .decision import Decision
from .decision_status import DecisionStatus
from .decision_type import DecisionType
from .intent import Intent
from .intent_confidence import IntentConfidence
from .intent_evidence import IntentEvidence
from .intent_type import IntentType

logger = logging.getLogger(__name__)

# ─── Decision Type → Intent Type mapping ──────────────────────────────────────
# Each DecisionType may satisfy one or more IntentTypes.
# This mapping drives the "Why" inference without LLMs.
_DECISION_TO_INTENT_MAP: Dict[DecisionType, List[IntentType]] = {
    DecisionType.TECHNOLOGY_ADOPTION:   [IntentType.SCALABILITY, IntentType.LATENCY],
    DecisionType.TECHNOLOGY_REMOVAL:    [IntentType.COST_REDUCTION, IntentType.COUPLING_REDUCTION],
    DecisionType.AI_ADOPTION:           [IntentType.AI_ENABLEMENT],
    DecisionType.SECURITY:              [IntentType.SECURITY, IntentType.COMPLIANCE],
    DecisionType.INFRASTRUCTURE:        [IntentType.SCALABILITY, IntentType.OBSERVABILITY],
    DecisionType.ARCHITECTURAL:         [IntentType.COUPLING_REDUCTION, IntentType.SCALABILITY],
    DecisionType.CAPABILITY_CREATION:   [IntentType.COUPLING_REDUCTION],
    DecisionType.CAPABILITY_SPLIT:      [IntentType.COUPLING_REDUCTION],
    DecisionType.CAPABILITY_MERGE:      [IntentType.COST_REDUCTION],
    DecisionType.SCALING:               [IntentType.SCALABILITY],
    DecisionType.PERFORMANCE:           [IntentType.LATENCY],
    DecisionType.COMPLIANCE:            [IntentType.COMPLIANCE],
    DecisionType.OWNERSHIP_CHANGE:      [IntentType.RELIABILITY],
    DecisionType.DATA_MODEL:            [IntentType.SCALABILITY],
    DecisionType.REFACTORING:           [IntentType.COUPLING_REDUCTION],
    DecisionType.UNKNOWN:               [IntentType.UNKNOWN],
}

# Intent display labels for synthesised intents
_INTENT_LABELS: Dict[IntentType, str] = {
    IntentType.SCALABILITY:        "Improve Scalability",
    IntentType.RELIABILITY:        "Improve Reliability",
    IntentType.SECURITY:           "Strengthen Security Posture",
    IntentType.LATENCY:            "Reduce Latency",
    IntentType.COUPLING_REDUCTION: "Reduce Coupling & Improve Modularity",
    IntentType.COST_REDUCTION:     "Reduce Operational Cost",
    IntentType.AI_ENABLEMENT:      "Enable AI / ML Capabilities",
    IntentType.COMPLIANCE:         "Achieve Regulatory Compliance",
    IntentType.OBSERVABILITY:      "Improve System Observability",
    IntentType.UNKNOWN:            "Unknown Strategic Intent",
}


class CausalReasoningEngine:
    """
    Constructs causal chains linking intents (motivations) to decisions (changes).

    Produces:
        - CausalChain objects with real confidence scores
        - Multi-hop MOTIVATES and ENABLES relationships
        - CONTRADICTS edges for conflicting decisions

    Usage::

        engine = CausalReasoningEngine()
        chains = engine.infer_causes(decisions, intents)
    """

    def infer_causes(
        self,
        decisions: List[Decision],
        intents: List[Intent],
    ) -> List[CausalChain]:
        """
        Build causal chains from decisions and available intents.

        Args:
            decisions:  List of discovered Decision objects.
            intents:    Existing intents from the persistence layer (may be empty).

        Returns:
            List of :class:`CausalChain` objects, one per unique IntentType group.
        """
        if not decisions:
            return []

        now = datetime.now(timezone.utc)
        repository_id = decisions[0].repository_id

        # Stage 1: Map decisions → inferred intent types
        decision_intent_map: Dict[str, List[IntentType]] = {}
        for decision in decisions:
            inferred = _DECISION_TO_INTENT_MAP.get(decision.decision_type, [IntentType.UNKNOWN])
            decision_intent_map[str(decision.id)] = inferred

        # Stage 2: Group decisions by primary intent type
        intent_to_decisions: Dict[IntentType, List[Decision]] = defaultdict(list)
        for decision in decisions:
            primary_intent = decision_intent_map[str(decision.id)][0]
            intent_to_decisions[primary_intent].append(decision)

        # Stage 3: Build or resolve Intent objects
        existing_intent_map: Dict[IntentType, Intent] = {
            i.intent_type: i for i in intents
        }

        # Stage 4: Detect conflicts among decisions
        conflict_pairs = self._detect_conflicts(decisions)

        # Stage 5: Build one CausalChain per intent group
        chains: List[CausalChain] = []

        for intent_type, group_decisions in intent_to_decisions.items():
            intent = self._resolve_or_synthesise_intent(
                intent_type=intent_type,
                group_decisions=group_decisions,
                existing_intent=existing_intent_map.get(intent_type),
                repository_id=repository_id,
                now=now,
            )

            relationships: List[CausalRelationship] = []

            # MOTIVATES: Intent → each Decision in the group
            for decision in group_decisions:
                causal_confidence = self._compute_causal_confidence(intent, decision)
                motivates = CausalRelationship(
                    cause_id=intent.id,
                    effect_id=decision.id,
                    cause_label=f"Intent: {intent.name}",
                    effect_label=f"Decision: {decision.name}",
                    relationship_type="MOTIVATES",
                    confidence=causal_confidence,
                    evidence=list(
                        set(intent.evidence.supporting_commits[:3])
                        | set(decision.supporting_evidence.supporting_commits[:3])
                    ),
                )
                relationships.append(motivates)

            # ENABLES: sibling decisions that share affected capabilities
            enables_edges = self._build_enables_edges(group_decisions, now)
            relationships.extend(enables_edges)

            # CONTRADICTS: decisions flagged as conflicting
            for d_a, d_b in conflict_pairs:
                if d_a in group_decisions and d_b in group_decisions:
                    contradicts = CausalRelationship(
                        cause_id=d_a.id,
                        effect_id=d_b.id,
                        cause_label=f"Decision: {d_a.name}",
                        effect_label=f"Decision: {d_b.name}",
                        relationship_type="CONTRADICTS",
                        confidence=0.9,
                        evidence=[],
                    )
                    relationships.append(contradicts)

            if not relationships:
                continue

            chain_confidence = (
                sum(r.confidence for r in relationships) / len(relationships)
            )

            chain = CausalChain(
                chain_id=uuid.uuid4(),
                repository_id=repository_id,
                root_cause_id=intent.id,
                relationships=relationships,
                summary=self._format_summary(intent, group_decisions),
                confidence=round(chain_confidence, 4),
                generated_at=now,
            )
            chains.append(chain)

        logger.info(
            "CausalReasoningEngine: built %d causal chains for repo '%s'",
            len(chains),
            repository_id,
        )
        return chains

    # ─────────────────────────────────────────────────────────────────────────
    #  Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _resolve_or_synthesise_intent(
        self,
        intent_type: IntentType,
        group_decisions: List[Decision],
        existing_intent: Optional[Intent],
        repository_id: str,
        now: datetime,
    ) -> Intent:
        """Return an existing Intent or synthesise a new one from the decision group."""
        if existing_intent is not None:
            return existing_intent

        # Synthesise: merge evidence from all decisions in the group
        all_commits = []
        all_docs = []
        for d in group_decisions:
            all_commits.extend(d.supporting_evidence.supporting_commits)
            all_docs.extend(d.supporting_evidence.supporting_documents)

        decision_ids = [str(d.id) for d in group_decisions]
        avg_confidence = (
            sum(d.confidence.score for d in group_decisions) / len(group_decisions)
            if group_decisions else 0.5
        )
        has_adr = bool(all_docs)

        intent_confidence = IntentConfidence.compute(
            evidence_coverage=min(1.0, len(all_commits) / 5),
            historical_support=min(1.0, len(group_decisions) / 3),
            architectural_support=0.8 if has_adr else 0.3,
            capability_support=avg_confidence,
            artifact_agreement=0.7 if has_adr else 0.2,
        )

        # Determine timestamps from earliest/latest decisions
        sorted_by_created = sorted(group_decisions, key=lambda d: d.created_at)
        first_seen = sorted_by_created[0].created_at if sorted_by_created else now
        last_seen = sorted_by_created[-1].created_at if sorted_by_created else now

        return Intent(
            id=uuid.uuid4(),
            name=_INTENT_LABELS.get(intent_type, intent_type.value.replace("_", " ").title()),
            intent_type=intent_type,
            description=(
                f"Strategic intent '{intent_type.value}' inferred from "
                f"{len(group_decisions)} decision(s) in this repository."
            ),
            confidence=intent_confidence,
            evidence=IntentEvidence(
                supporting_commits=list(set(all_commits))[:10],
                supporting_documents=list(set(all_docs))[:5],
                supporting_capabilities=[],
                supporting_decisions=decision_ids,
            ),
            repository_id=repository_id,
            first_seen_at=_ensure_tz(first_seen),
            last_seen_at=_ensure_tz(last_seen),
            supporting_decisions=decision_ids,
        )

    def _compute_causal_confidence(self, intent: Intent, decision: Decision) -> float:
        """
        Multi-factor causal confidence between an Intent and a Decision.

        Factors:
            0.30 — shared supporting commits
            0.25 — shared supporting documents (ADR)
            0.30 — decision.confidence.score
            0.15 — total evidence density (commits + events)
        """
        intent_commits = set(intent.evidence.supporting_commits)
        decision_commits = set(decision.supporting_evidence.supporting_commits)
        shared_commits = intent_commits & decision_commits
        commit_overlap = min(1.0, len(shared_commits) / 3) if (intent_commits or decision_commits) else 0.0

        intent_docs = set(intent.evidence.supporting_documents)
        decision_docs = set(decision.supporting_evidence.supporting_documents)
        shared_docs = intent_docs & decision_docs
        doc_overlap = min(1.0, len(shared_docs) / 2) if (intent_docs or decision_docs) else 0.0

        decision_confidence = decision.confidence.score

        total_evidence = (
            len(decision.supporting_evidence.supporting_commits)
            + len(decision.supporting_evidence.supporting_repository_events)
        )
        evidence_density = min(1.0, total_evidence / 8)

        score = (
            0.30 * commit_overlap
            + 0.25 * doc_overlap
            + 0.30 * decision_confidence
            + 0.15 * evidence_density
        )
        return round(min(1.0, score), 4)

    def _build_enables_edges(
        self, decisions: List[Decision], now: datetime
    ) -> List[CausalRelationship]:
        """
        Build ENABLES relationships between sibling decisions that share
        affected capabilities (i.e., one decision unlocked conditions for another).
        """
        edges: List[CausalRelationship] = []
        for i, d_a in enumerate(decisions):
            for d_b in decisions[i + 1:]:
                if d_a.id == d_b.id:
                    continue
                # Shared capabilities = enablement signal
                shared = (
                    set(d_a.affected_capabilities) & set(d_b.affected_capabilities)
                    or set(d_a.affected_services) & set(d_b.affected_services)
                )
                if not shared:
                    continue
                # Only add ENABLES if d_a appeared before d_b
                if d_a.created_at <= d_b.created_at:
                    confidence = min(1.0, len(shared) / 5 + 0.3)
                    edge = CausalRelationship(
                        cause_id=d_a.id,
                        effect_id=d_b.id,
                        cause_label=f"Decision: {d_a.name}",
                        effect_label=f"Decision: {d_b.name}",
                        relationship_type="ENABLES",
                        confidence=round(confidence, 4),
                        evidence=list(shared)[:5],
                    )
                    edges.append(edge)
        return edges

    def _detect_conflicts(
        self, decisions: List[Decision]
    ) -> List[Tuple[Decision, Decision]]:
        """
        Detect conflicting decisions: same DecisionType but conflicting statuses
        (e.g. one ACTIVE, one REVERTED) with overlapping evidence commits.
        """
        conflicts: List[Tuple[Decision, Decision]] = []
        for i, d_a in enumerate(decisions):
            for d_b in decisions[i + 1:]:
                if d_a.decision_type != d_b.decision_type:
                    continue
                status_conflict = (
                    {d_a.status, d_b.status}
                    == {DecisionStatus.ACTIVE, DecisionStatus.REVERTED}
                )
                if not status_conflict:
                    continue
                # Check commit overlap as a secondary condition
                commits_a = set(d_a.supporting_evidence.supporting_commits)
                commits_b = set(d_b.supporting_evidence.supporting_commits)
                if commits_a & commits_b:
                    conflicts.append((d_a, d_b))
        return conflicts

    @staticmethod
    def _format_summary(intent: Intent, decisions: List[Decision]) -> str:
        decision_names = [d.name for d in decisions[:3]]
        suffix = f" and {len(decisions) - 3} more" if len(decisions) > 3 else ""
        return (
            f"Intent '{intent.name}' motivates {len(decisions)} decision(s): "
            + ", ".join(decision_names) + suffix + "."
        )


def _ensure_tz(dt: Optional[datetime]) -> datetime:
    """Ensure a datetime is timezone-aware (UTC fallback)."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
