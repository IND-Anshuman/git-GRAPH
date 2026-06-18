"""
Phase 7A — MultiHopReasoningEngine

A helper engine that executes targeted *n*-hop queries over the relationship
graph starting from a specific source node.

Unlike ``EvidenceExpansionEngine`` (which broad-sweeps all entity-type
evidence), ``MultiHopReasoningEngine`` is called on demand by strategies that
need to trace a precise path (e.g. RootCauseStrategy tracing a causal chain).

Algorithm
---------
BFS traversal from a seed SEID up to *max_hops* levels.  Each hop records
a ``HopResult`` with the discovered neighbour SEIDs and the relationship types
traversed.

Returns a ``MultiHopTrace`` — a lightweight record of the full traversal
path including all discovered SEIDs and the relationship types on each edge.
"""

from __future__ import annotations

import uuid
import logging
from dataclasses import dataclass, field
from typing import Any

from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class HopResult:
    """One hop level in a multi-hop traversal."""
    hop: int
    source_seid: str
    discovered_seids: list[str] = field(default_factory=list)
    relationship_types: list[str] = field(default_factory=list)


@dataclass
class MultiHopTrace:
    """Full record of a multi-hop traversal from a seed SEID."""
    seed_seid: str
    max_hops: int
    hops: list[HopResult] = field(default_factory=list)
    all_discovered: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed_seid": self.seed_seid,
            "max_hops": self.max_hops,
            "total_discovered": len(self.all_discovered),
            "hops": [
                {
                    "hop": h.hop,
                    "source": h.source_seid,
                    "discovered": h.discovered_seids,
                    "rel_types": h.relationship_types,
                }
                for h in self.hops
            ],
        }


def _to_uuid(val: Any) -> uuid.UUID | None:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, AttributeError):
        return None


class MultiHopReasoningEngine:
    """BFS-based multi-hop traversal engine for targeted path tracing.

    Usage::

        engine = MultiHopReasoningEngine()
        trace = engine.trace(seed_seid="...", uow=uow, max_hops=3)
    """

    def trace(
        self,
        seed_seid: str,
        uow: IUnitOfWork,
        max_hops: int = 2,
        direction: str = "both",  # "outbound", "inbound", "both"
    ) -> MultiHopTrace:
        """Execute a BFS traversal from *seed_seid* for up to *max_hops* hops.

        Args:
            seed_seid: Starting entity SEID string.
            uow:       Open Unit of Work.
            max_hops:  Maximum hop depth.
            direction: Traversal direction — ``"outbound"``, ``"inbound"``,
                       or ``"both"``.

        Returns:
            A :class:`MultiHopTrace` with all discovered SEIDs.
        """
        trace = MultiHopTrace(seed_seid=seed_seid, max_hops=max_hops)
        visited: set[str] = {seed_seid}
        frontier: list[str] = [seed_seid]

        for hop_index in range(max_hops):
            if not frontier:
                break

            hop_result = HopResult(hop=hop_index + 1, source_seid=",".join(frontier[:5]))
            next_frontier: list[str] = []

            for seid_str in frontier:
                seid_uuid = _to_uuid(seid_str)
                if seid_uuid is None:
                    continue

                if direction in ("outbound", "both"):
                    try:
                        rels = uow.relationships.get_by_source(seid_uuid)  # type: ignore[attr-defined]
                        for rel in rels:
                            target = str(getattr(rel, "target_seid", None) or "")
                            rel_type = str(getattr(rel, "relationship_type", "unknown"))
                            if target and target not in visited:
                                visited.add(target)
                                next_frontier.append(target)
                                trace.all_discovered.append(target)
                                hop_result.discovered_seids.append(target)
                                hop_result.relationship_types.append(rel_type)
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("MultiHop outbound failed for %s: %s", seid_str, exc)

                if direction in ("inbound", "both"):
                    try:
                        rels = uow.relationships.get_by_target(seid_uuid)  # type: ignore[attr-defined]
                        for rel in rels:
                            source = str(getattr(rel, "source_seid", None) or "")
                            rel_type = str(getattr(rel, "relationship_type", "unknown"))
                            if source and source not in visited:
                                visited.add(source)
                                next_frontier.append(source)
                                trace.all_discovered.append(source)
                                hop_result.discovered_seids.append(source)
                                hop_result.relationship_types.append(rel_type)
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("MultiHop inbound failed for %s: %s", seid_str, exc)

            trace.hops.append(hop_result)
            frontier = next_frontier

        return trace
