"""
Phase 7A — EvidenceExpansionEngine

Performs cycle-safe multi-hop graph traversal over the relationship graph
to expand the initial collected evidence set to its transitive neighbours.

Algorithm
---------
1. Start from the set of entity SEIDs already in ``context.expanded_evidence``.
2. For each entity SEID, load outbound and inbound relationships from the UoW.
3. For each new SEID discovered, add a new ``ReasoningEvidence`` node and
   recurse up to ``max_hops`` levels deep.
4. Track visited node IDs in a set to prevent cycles.

Max hop limits
--------------
WHY / ARCHITECTURE  → 2 hops (narrow, focused)
ROOT_CAUSE          → 3 hops (deeper dependency traversal)
BLAST_RADIUS        → 3 hops (full transitive impact)

Notes
-----
* Expansion is purely additive — it never removes existing evidence.
* Each hop adds a chain step for full audit-trail visibility.
* Cycle protection is O(1) per node using a visited set.
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.evidence_weight_registry import EvidenceWeightRegistry
from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


def _to_uuid(val: Any) -> uuid.UUID | None:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, AttributeError):
        return None


class EvidenceExpansionEngine:
    """Multi-hop relationship traversal expanding the initial evidence set."""

    def expand(
        self,
        context: ReasoningContext,
        uow: IUnitOfWork,
        max_hops: int = 2,
    ) -> None:
        """Expand ``context.expanded_evidence`` by walking the relationship graph.

        Args:
            context:  Mutable pipeline carry-bag (modified in-place).
            uow:      Open Unit of Work.
            max_hops: Maximum relationship hops to walk.
        """
        visited: set[str] = {ev.source_id for ev in context.expanded_evidence}
        frontier: list[str] = [
            ev.source_id
            for ev in context.expanded_evidence
            if ev.source_type == "entity"
        ]

        context.chain.add_step(
            step_type="evidence_expansion_start",
            description=(
                f"EvidenceExpansionEngine: starting from {len(frontier)} entity nodes, "
                f"max_hops={max_hops}."
            ),
            inputs=frontier[:10],
        )

        for hop in range(max_hops):
            if not frontier:
                break

            next_frontier: list[str] = []

            for seid_str in frontier:
                seid_uuid = _to_uuid(seid_str)
                if seid_uuid is None:
                    continue

                try:
                    outbound = uow.relationships.get_by_source(seid_uuid)  # type: ignore[attr-defined]
                    for rel in outbound:
                        target = str(getattr(rel, "target_seid", None) or "")
                        if target and target not in visited:
                            visited.add(target)
                            next_frontier.append(target)
                            context.expanded_evidence.append(ReasoningEvidence(
                                source_id=target,
                                source_type="entity",
                                description=f"Expanded from {seid_str} via {getattr(rel, 'relationship_type', 'unknown')}",
                                weight=EvidenceWeightRegistry.ENTITY * (0.9 ** (hop + 1)),
                            ))
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Outbound expansion failed for %s: %s", seid_str, exc)

                try:
                    inbound = uow.relationships.get_by_target(seid_uuid)  # type: ignore[attr-defined]
                    for rel in inbound:
                        source = str(getattr(rel, "source_seid", None) or "")
                        if source and source not in visited:
                            visited.add(source)
                            next_frontier.append(source)
                            context.expanded_evidence.append(ReasoningEvidence(
                                source_id=source,
                                source_type="entity",
                                description=f"Inbound from {seid_str} via {getattr(rel, 'relationship_type', 'unknown')}",
                                weight=EvidenceWeightRegistry.ENTITY * (0.9 ** (hop + 1)),
                            ))
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Inbound expansion failed for %s: %s", seid_str, exc)

            context.chain.add_step(
                step_type=f"evidence_expansion_hop_{hop + 1}",
                description=(
                    f"Hop {hop + 1}: discovered {len(next_frontier)} new node(s). "
                    f"Total evidence: {len(context.expanded_evidence)}."
                ),
                outputs=next_frontier[:10],
            )
            frontier = next_frontier

        context.chain.add_step(
            step_type="evidence_expansion_complete",
            description=(
                f"Expansion complete. Total evidence nodes: {len(context.expanded_evidence)}."
            ),
        )
