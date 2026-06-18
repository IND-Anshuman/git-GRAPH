"""
Phase 7A — EvidenceCollectionEngine

Fetches targeted raw evidence from the UoW based on the ``QueryPlan``
produced by the ``QueryPlanner``.

Scope-to-UoW mapping
---------------------
  "entities"      → uow.code_entities.get_by_repository(repo_id)
  "relationships" → uow.relationships.get_by_repository(repo_id)
  "concepts"      → uow.concept_nodes.list_by_repository(repo_id)
  "capabilities"  → uow.capabilities.list_by_repository(repo_id)
  "artifacts"     → uow.knowledge_artifacts.list_by_repository(repo_id)
  "flows" / "ownership" / "timeline"  → best-effort from artifacts

Data is stored as raw dicts in ``ReasoningContext`` so that the rest of
the pipeline does not depend on domain entity types.  This also makes the
collection engine easy to unit-test with in-memory stubs.
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from src.application.reasoning.query_planner import QueryPlan
from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


def _safe_uuid(value: Any) -> uuid.UUID | None:
    """Return a UUID from a string or UUID, or None on failure."""
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError):
        return None


def _entity_to_dict(entity: Any) -> dict[str, Any]:
    """Coerce a domain entity or ORM model to a plain dict."""
    if isinstance(entity, dict):
        return entity
    if hasattr(entity, "__dict__"):
        return {k: v for k, v in entity.__dict__.items() if not k.startswith("_")}
    return {"id": str(entity)}


class EvidenceCollectionEngine:
    """Collects raw evidence from the knowledge graph based on a QueryPlan.

    All collected data is stored in the ``ReasoningContext`` carry-bag so
    that downstream engines can work without touching the UoW directly.
    """

    def collect(self, context: ReasoningContext, plan: QueryPlan, uow: IUnitOfWork) -> None:
        """Populate *context* data lists according to *plan.collect_scopes*.

        Args:
            context: Mutable pipeline carry-bag (modified in-place).
            plan:    QueryPlan from the QueryPlanner.
            uow:     Open Unit of Work (caller must manage the session).
        """
        repo_id = _safe_uuid(context.repository_id)
        if repo_id is None:
            logger.warning(
                "EvidenceCollectionEngine: invalid repository_id=%r; skipping collection.",
                context.repository_id,
            )
            context.chain.add_step(
                step_type="evidence_collection",
                description="SKIPPED — invalid repository_id.",
            )
            return

        context.chain.add_step(
            step_type="evidence_collection",
            description=(
                f"Collecting evidence for scopes={plan.collect_scopes}, "
                f"target={plan.target_term!r}, repo={context.repository_id}"
            ),
            inputs=[context.repository_id],
        )

        scopes = set(plan.collect_scopes)
        collected_ids: list[str] = []

        # ── Entities ──────────────────────────────────────────────────────────
        if "entities" in scopes:
            try:
                entities = uow.code_entities.get_by_repository(repo_id)
                context.entities = [_entity_to_dict(e) for e in entities]
                # Build evidence nodes
                for e in entities:
                    d = _entity_to_dict(e)
                    eid = str(d.get("seid") or d.get("id") or "")
                    if eid:
                        context.expanded_evidence.append(ReasoningEvidence(
                            source_id=eid,
                            source_type="entity",
                            description=str(d.get("name") or d.get("qualified_name") or eid),
                            weight=EvidenceWeightRegistry.ENTITY,
                        ))
                        collected_ids.append(eid)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Entity collection failed: %s", exc)

        # ── Relationships ─────────────────────────────────────────────────────
        if "relationships" in scopes:
            try:
                rels = uow.relationships.get_by_repository(repo_id)
                context.relationships = [_entity_to_dict(r) for r in rels]
                for r in rels:
                    d = _entity_to_dict(r)
                    rid = str(d.get("id") or "")
                    if rid:
                        context.expanded_evidence.append(ReasoningEvidence(
                            source_id=rid,
                            source_type="relationship",
                            description=(
                                f"{d.get('relationship_type', 'rel')} "
                                f"{d.get('source_seid','?')} → {d.get('target_seid','?')}"
                            ),
                            weight=EvidenceWeightRegistry.RELATIONSHIP,
                        ))
                        collected_ids.append(rid)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Relationship collection failed: %s", exc)

        # ── Concepts ──────────────────────────────────────────────────────────
        if "concepts" in scopes:
            try:
                concepts = uow.concept_nodes.list_by_repository(repo_id)
                context.concepts = [_entity_to_dict(c) for c in concepts]
                for c in concepts:
                    d = _entity_to_dict(c)
                    cid = str(d.get("id") or "")
                    if cid:
                        context.expanded_evidence.append(ReasoningEvidence(
                            source_id=cid,
                            source_type="concept",
                            description=str(d.get("name") or cid),
                            weight=EvidenceWeightRegistry.CONCEPT,
                        ))
                        collected_ids.append(cid)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Concept collection failed: %s", exc)

        # ── Capabilities ──────────────────────────────────────────────────────
        if "capabilities" in scopes:
            try:
                caps = uow.capabilities.list_by_repository(repo_id)
                context.capabilities = [_entity_to_dict(c) for c in caps]
                for cap in caps:
                    d = _entity_to_dict(cap)
                    cid = str(d.get("id") or "")
                    if cid:
                        context.expanded_evidence.append(ReasoningEvidence(
                            source_id=cid,
                            source_type="capability",
                            description=str(d.get("name") or cid),
                            weight=EvidenceWeightRegistry.CAPABILITY,
                        ))
                        collected_ids.append(cid)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Capability collection failed: %s", exc)

        # ── Artifacts (covers flows, timeline, ownership) ─────────────────────
        if any(s in scopes for s in ("artifacts", "flows", "timeline", "ownership")):
            try:
                artifacts = uow.knowledge_artifacts.list_by_repository(repo_id)
                context.artifacts = [_entity_to_dict(a) for a in artifacts]
                for art in artifacts:
                    d = _entity_to_dict(art)
                    aid = str(d.get("id") or "")
                    art_type = str(d.get("artifact_type") or "artifact")
                    if aid:
                        weight = EvidenceWeightRegistry.get(art_type)
                        context.expanded_evidence.append(ReasoningEvidence(
                            source_id=aid,
                            source_type=art_type,
                            description=f"Artifact type={art_type}",
                            weight=weight,
                        ))
                        collected_ids.append(aid)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Artifact collection failed: %s", exc)

        context.chain.add_step(
            step_type="evidence_collection_summary",
            description=(
                f"Collected {len(context.expanded_evidence)} evidence nodes across "
                f"{len(scopes)} scope(s)."
            ),
            outputs=collected_ids[:20],  # log up to 20 for brevity
        )
