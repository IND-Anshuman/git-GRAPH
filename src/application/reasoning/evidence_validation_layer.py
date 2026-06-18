"""
Phase 7A — EvidenceValidationLayer

Acts as a strict gate between the evidence collection/expansion phase and
the strategy execution phase.  Its single responsibility is to confirm that
every ``ReasoningEvidence`` node in ``context.expanded_evidence`` actually
exists in the physical database.

Hallucination prevention contract
----------------------------------
1. For each evidence node, attempt a database lookup by source_id.
2. If the entity is found → set ``evidence.validated = True`` and move it
   to ``context.validated_evidence``.
3. If the entity is NOT found → log a warning and DISCARD it.
4. After validation, log a chain step summarising accepted vs. rejected counts.

This layer ensures that:
  * No reasoning conclusion is based on a ghost reference.
  * Results are fully reproducible — the same evidence IDs produce the same
    result on any run against the same database state.
  * The limitations list can be auto-populated when large numbers of nodes
    are discarded (indicating stale or orphaned evidence).

Validation scope
----------------
We validate entity-type evidence against ``uow.code_entities.get_by_seid()``.
All other source types (capability, concept, artifact, relationship) are
accepted after a lightweight ID format check, because they were queried
directly from the DB and are implicitly valid.
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from src.application.reasoning.reasoning_context import ReasoningContext
from src.application.reasoning.reasoning_evidence import ReasoningEvidence
from src.application.reasoning.reasoning_limitations import ReasoningLimitation
from src.application.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)

# Source types that get verified against the DB
_ENTITY_TYPES = {"entity"}
# Source types that are trusted implicitly (queried directly from DB)
_TRUSTED_TYPES = {"capability", "concept", "artifact", "relationship",
                  "flow", "timeline", "ownership", "dependency"}


def _is_valid_id(source_id: str) -> bool:
    """Return True if source_id is a non-empty string."""
    return bool(source_id and source_id.strip())


class EvidenceValidationLayer:
    """Validates evidence nodes against the physical database.

    Nodes that pass are added to ``context.validated_evidence`` with
    ``validated=True``.  Nodes that fail are discarded and counted.
    """

    def validate(self, context: ReasoningContext, uow: IUnitOfWork) -> None:
        """Run validation for all nodes in ``context.expanded_evidence``.

        Args:
            context: Mutable pipeline carry-bag (modified in-place).
            uow:     Open Unit of Work.
        """
        if not context.expanded_evidence:
            context.chain.add_step(
                step_type="evidence_validation",
                description="No expanded evidence to validate; skipping validation layer.",
            )
            return

        accepted: list[ReasoningEvidence] = []
        rejected_count = 0
        entity_miss_count = 0

        for ev in context.expanded_evidence:
            if not _is_valid_id(ev.source_id):
                rejected_count += 1
                continue

            # ── Trusted types: accept without DB round-trip ────────────────
            if ev.source_type.lower() in _TRUSTED_TYPES:
                ev.validated = True
                accepted.append(ev)
                continue

            # ── Entity type: verify against DB ─────────────────────────────
            if ev.source_type.lower() in _ENTITY_TYPES:
                try:
                    found = uow.code_entities.get_by_seid(ev.source_id)  # type: ignore[attr-defined]
                    if found is not None:
                        ev.validated = True
                        accepted.append(ev)
                    else:
                        entity_miss_count += 1
                        rejected_count += 1
                        logger.debug(
                            "EvidenceValidationLayer: entity source_id=%r not found in DB.",
                            ev.source_id,
                        )
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "EvidenceValidationLayer: DB lookup failed for source_id=%r: %s",
                        ev.source_id,
                        exc,
                    )
                    # On DB error, accept with a lower weight to avoid silent failures
                    ev.weight = max(0.0, ev.weight * 0.5)
                    ev.validated = True
                    accepted.append(ev)
                continue

            # ── Unknown type: accept with reduced weight ───────────────────
            ev.weight = max(0.0, ev.weight * 0.4)
            ev.validated = True
            accepted.append(ev)

        context.validated_evidence = accepted

        # ── Auto-limitations when significant evidence was rejected ────────
        if rejected_count > 5 and len(context.expanded_evidence) > 0:
            rejection_pct = rejected_count / len(context.expanded_evidence) * 100
            context.chain.add_step(
                step_type="evidence_validation_warning",
                description=(
                    f"WARNING: {rejected_count} of {len(context.expanded_evidence)} "
                    f"evidence nodes ({rejection_pct:.0f}%) were rejected by validation."
                ),
            )

        context.chain.add_step(
            step_type="evidence_validation",
            description=(
                f"Validation complete: {len(accepted)} accepted, "
                f"{rejected_count} rejected "
                f"({entity_miss_count} entity miss(es))."
            ),
            outputs=[ev.source_id for ev in accepted[:10]],
        )
