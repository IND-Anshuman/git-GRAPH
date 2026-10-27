"""Detect architecture styles from measurable properties of the code graph.

Each style in the pattern registry is a *signature* of signals that can be
measured on an :class:`ArchitectureGraph`:

* **topology** - required layers present, or module structure;
* **dependency direction** - share of cross-layer edges that respect the
  style's layer ranking, penalised by dependency cycles;
* **roles** - identifier sub-words (``controller``, ``port``, ``publisher``)
  that characterise the style, counted on node names and file paths;
* **flow** - the runtime-flow subset of those roles.

Only signals a signature defines are scored; ownership and history are not
observed here, so they are reported as unavailable instead of being filled
with a constant. If no style clears ``min_confidence`` the result is
``UNKNOWN``, which is the honest answer for small or unstructured graphs.
"""

from __future__ import annotations

import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.application.semantic.embedding.lexical_embedding import tokenize

from .architecture_confidence import ArchitectureConfidence
from .architecture_evidence import ArchitectureEvidence
from .architecture_graph import ArchitectureGraph
from .architecture_pattern_registry import ArchitecturePatternRegistry
from .architecture_profile import ArchitectureProfile
from .architecture_type import ArchitectureType

MIN_CONFIDENCE = 0.5
MIN_CROSS_LAYER_EDGES = 3


@dataclass
class GraphFeatures:
    """Pattern-independent measurements, computed once per graph."""

    node_count: int
    layers: Counter
    node_tokens: dict[str, set[str]]
    cyclicity: float
    modules: Counter
    cross_module_ratio: float | None
    edges: list[tuple[str, str]] = field(default_factory=list)
    node_layers: dict[str, str] = field(default_factory=dict)


@dataclass
class PatternScore:
    name: str
    confidence: ArchitectureConfidence
    signals: list[str]
    matched_nodes: set[str]
    components: int


class ArchitectureReasoningEngine:
    """Scores every registered architecture signature against a graph."""

    def __init__(
        self, pattern_registry: ArchitecturePatternRegistry, min_confidence: float = MIN_CONFIDENCE
    ) -> None:
        self.pattern_registry = pattern_registry
        self.min_confidence = min_confidence

    def detect_architecture(
        self, repository_id: str, commit_hash: str, graph: ArchitectureGraph
    ) -> ArchitectureProfile:
        features = self.extract_features(graph)
        scores = [
            self.score_pattern(name, data, features)
            for name, data in sorted(self.pattern_registry.get_all_patterns().items())
            if isinstance(data, dict)
        ]
        # Highest score wins; on ties prefer the more specific signature.
        scores.sort(key=lambda s: (s.confidence.score, s.components), reverse=True)
        best = scores[0] if scores else None

        if best is None or features.node_count == 0 or best.confidence.score < self.min_confidence:
            confidence = best.confidence if best else ArchitectureConfidence.compute(0, 0, 0, 0, 0, 0, 0)
            if features.node_count == 0:
                confidence = ArchitectureConfidence.compute(0, 0, 0, 0, 0, 0, 0)
            runner_up = f" Closest match: {best.name} ({best.confidence.score:.2f})." if best else ""
            return ArchitectureProfile(
                id=uuid.uuid4(),
                architecture_type=ArchitectureType.UNKNOWN,
                confidence=confidence,
                description=f"No architecture signature reached {self.min_confidence:.2f} confidence.{runner_up}",
                evidence=ArchitectureEvidence(violating_patterns=[s.name for s in scores[:3]]),
                detected_at=datetime.now(UTC),
                repository_id=repository_id,
                commit_hash=commit_hash,
            )

        try:
            arch_type = ArchitectureType[best.name.upper()]
        except KeyError:
            arch_type = ArchitectureType.UNKNOWN
        evidence = ArchitectureEvidence(
            supporting_patterns=[best.name],
            violating_patterns=[s.name for s in scores[1:4] if s.confidence.score >= self.min_confidence],
            entities=[
                {"node_id": nid, "label": graph.nodes[nid].label}
                for nid in sorted(best.matched_nodes)[:50]
                if nid in graph.nodes
            ],
            dependency_paths=graph.detect_cycles()[:10],
            capabilities=[{"signal": s} for s in best.signals],
        )
        return ArchitectureProfile(
            id=uuid.uuid4(),
            architecture_type=arch_type,
            confidence=best.confidence,
            description=f"Detected {arch_type.value} architecture: " + "; ".join(best.signals),
            evidence=evidence,
            detected_at=datetime.now(UTC),
            repository_id=repository_id,
            commit_hash=commit_hash,
        )

    # ── features ─────────────────────────────────────────────────────
    @staticmethod
    def extract_features(graph: ArchitectureGraph) -> GraphFeatures:
        layers: Counter = Counter()
        modules: Counter = Counter()
        node_tokens: dict[str, set[str]] = {}
        node_layers: dict[str, str] = {}
        for node_id, node in graph.nodes.items():
            meta = node.metadata or {}
            if meta.get("layer"):
                layer = str(meta["layer"]).lower()
                layers[layer] += 1
                node_layers[node_id] = layer
            if meta.get("module"):
                modules[str(meta["module"])] += 1
            text = " ".join(
                str(x) for x in (node.label, meta.get("file_path", ""), meta.get("qualified_name", ""))
            )
            node_tokens[node_id] = set(tokenize(text))

        in_cycles = {n for cycle in graph.detect_cycles() for n in cycle}
        cyclicity = len(in_cycles) / len(graph.nodes) if graph.nodes else 0.0

        dep_edges = [
            (e.from_id, e.to_id)
            for e in graph.edges
            if e.relationship not in ArchitectureGraph.NON_DEPENDENCY_RELATIONSHIPS
        ]
        cross_ratio = None
        module_edges = [
            (graph.nodes[a].metadata.get("module"), graph.nodes[b].metadata.get("module"))
            for a, b in dep_edges
            if a in graph.nodes and b in graph.nodes
        ]
        module_edges = [(a, b) for a, b in module_edges if a and b]
        if module_edges:
            cross_ratio = sum(1 for a, b in module_edges if a != b) / len(module_edges)

        return GraphFeatures(
            node_count=len(graph.nodes),
            layers=layers,
            node_tokens=node_tokens,
            cyclicity=cyclicity,
            modules=modules,
            cross_module_ratio=cross_ratio,
            edges=dep_edges,
            node_layers=node_layers,
        )

    # ── scoring ──────────────────────────────────────────────────────
    def score_pattern(self, name: str, data: dict[str, Any], f: GraphFeatures) -> PatternScore:
        signals: list[str] = []
        matched: set[str] = set()
        available: set[str] = {"evidence"}
        topology = dependency = capability = flow = 0.0

        required_layers = [str(x).lower() for x in data.get("required_layers", [])]
        if required_layers:
            available.add("topology")
            present = [layer for layer in required_layers if f.layers.get(layer)]
            topology = len(present) / len(required_layers)
            signals.append(
                f"{len(present)}/{len(required_layers)} required layers present ({', '.join(present) or 'none'})"
            )

        modules_cfg = data.get("modules")
        if modules_cfg:
            available.add("topology")
            count = len([m for m, n in f.modules.items() if n >= 2])
            enough = min(1.0, count / max(1, modules_cfg.get("min_modules", 3)))
            ratio = f.cross_module_ratio
            limit = modules_cfg.get("max_cross_module_edge_ratio", 0.35)
            coupling = (
                0.0 if ratio is None else max(0.0, 1.0 - max(0.0, ratio - limit) / max(1e-9, 1.0 - limit))
            )
            topology = enough * coupling
            ratio_text = "n/a" if ratio is None else f"{ratio:.0%}"
            signals.append(f"{count} modules, {ratio_text} of dependencies cross module boundaries")

        rank = {str(k).lower(): v for k, v in (data.get("layer_rank") or {}).items()}
        if rank:
            cross = []
            for a, b in f.edges:
                la, lb = self._layer_of(a, f), self._layer_of(b, f)
                if la in rank and lb in rank and la != lb:
                    cross.append(rank[lb] >= rank[la])
            if len(cross) >= MIN_CROSS_LAYER_EDGES:
                available.add("dependency")
                dependency = sum(cross) / len(cross)
                signals.append(
                    f"{dependency:.0%} of {len(cross)} cross-layer dependencies follow the expected direction"
                )

        max_cyc = data.get("max_cyclicity")
        if max_cyc is not None and f.cyclicity > max_cyc:
            penalty = min(1.0, (f.cyclicity - max_cyc) / max(1e-9, 1.0 - max_cyc))
            dependency *= 1.0 - 0.5 * penalty
            topology *= 1.0 - 0.5 * penalty
            signals.append(f"{f.cyclicity:.0%} of components sit in dependency cycles (limit {max_cyc:.0%})")

        roles: dict[str, list[str]] = data.get("roles") or {}
        if roles:
            available.add("capability")
            found: dict[str, int] = {}
            for role, tokens in roles.items():
                token_set = {str(t).lower() for t in tokens}
                hits = {nid for nid, toks in f.node_tokens.items() if toks & token_set}
                if hits:
                    found[role] = len(hits)
                    matched |= hits
            required = data.get("roles_required", len(roles))
            capability = min(1.0, len(found) / max(1, required))
            listed = ", ".join(f"{r} ({n})" for r, n in sorted(found.items())) or "none"
            signals.append(f"roles found: {listed}")

            flow_roles = data.get("flow_roles") or []
            if flow_roles:
                available.add("flow")
                flow = sum(1 for r in flow_roles if r in found) / len(flow_roles)

        structural_layers = set(required_layers) | set(rank)
        matched |= {nid for nid, layer in f.node_layers.items() if layer in structural_layers}
        coverage = len(matched) / f.node_count if f.node_count else 0.0

        confidence = ArchitectureConfidence.compute(
            topology_match=topology,
            dependency_match=dependency,
            flow_match=flow,
            capability_match=capability,
            ownership_match=0.0,
            historical_match=0.0,
            evidence_coverage=coverage,
            available=available,
        )
        return PatternScore(name, confidence, signals, matched, len(available))

    @staticmethod
    def _layer_of(node_id: str, f: GraphFeatures) -> str | None:
        return f.node_layers.get(node_id)
