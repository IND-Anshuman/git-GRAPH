"""
Phase 7C — DecisionGraph

A pure-Python in-memory directed graph over Decision and CausalChain objects.

Capabilities:
    - Root detection (decisions with no inbound dependency edges)
    - Leaf detection (decisions with no outbound dependency edges)
    - Topological sort (Kahn's algorithm — respects dependency order)
    - Path traversal (DFS from a source node)
    - Cycle detection (identifies circular decision dependencies)
    - Adjacency serialisation (for external visualization / debugging)

The DecisionGraph is built from:
    - A list of Decision domain objects (nodes)
    - A list of DecisionDependency / CausalRelationship (edges)

It does NOT persist — it is a runtime compute structure rebuilt on demand.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from .decision import Decision

logger = logging.getLogger(__name__)


class DecisionGraph:
    """
    Directed dependency graph over :class:`Decision` nodes.

    Nodes:     Decision objects (keyed by str(id))
    Edges:     (source_id, target_id, relationship_type, confidence)

    Usage::

        graph = DecisionGraph(decisions, dependencies)
        roots = graph.get_roots()
        order = graph.topological_sort()
        path = graph.find_path(str(source_id), str(target_id))
        cycles = graph.detect_cycles()
    """

    def __init__(
        self,
        decisions: List[Decision],
        dependencies: List[Any],  # List of edge-like objects with source/target attributes
    ) -> None:
        self._nodes: Dict[str, Decision] = {str(d.id): d for d in decisions}

        # Adjacency lists: outbound and inbound
        self._outbound: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        self._inbound: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)

        for dep in (dependencies or []):
            src = str(getattr(dep, "source_decision_id", "") or getattr(dep, "cause_id", ""))
            tgt = str(getattr(dep, "target_decision_id", "") or getattr(dep, "effect_id", ""))
            rel = getattr(dep, "relationship_type", "DEPENDS_ON")
            conf = float(getattr(dep, "confidence", 1.0))

            if src and tgt and src in self._nodes and tgt in self._nodes:
                self._outbound[src].append((tgt, rel, conf))
                self._inbound[tgt].append((src, rel, conf))

        logger.debug(
            "DecisionGraph: %d nodes, %d edges",
            len(self._nodes),
            sum(len(v) for v in self._outbound.values()),
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  Node access
    # ─────────────────────────────────────────────────────────────────────────

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self._nodes.get(decision_id)

    def all_decisions(self) -> List[Decision]:
        return list(self._nodes.values())

    # ─────────────────────────────────────────────────────────────────────────
    #  Root / Leaf detection
    # ─────────────────────────────────────────────────────────────────────────

    def get_roots(self) -> List[Decision]:
        """
        Return decisions that have NO inbound dependency edges.

        These are the foundational decisions — no other decisions in the graph
        depend on them as prerequisites.
        """
        return [
            self._nodes[node_id]
            for node_id in self._nodes
            if not self._inbound.get(node_id)
        ]

    def get_leaves(self) -> List[Decision]:
        """
        Return decisions that have NO outbound dependency edges.

        These are terminal decisions — they depend on others but nothing depends on them.
        """
        return [
            self._nodes[node_id]
            for node_id in self._nodes
            if not self._outbound.get(node_id)
        ]

    # ─────────────────────────────────────────────────────────────────────────
    #  Traversal
    # ─────────────────────────────────────────────────────────────────────────

    def topological_sort(self) -> List[Decision]:
        """
        Return decisions in topological order using Kahn's algorithm.

        Decisions with no prerequisites come first.
        If the graph has cycles, the remaining cyclic nodes are appended at
        the end (after cycle detection logs a warning).
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self._nodes}
        for node_id in self._outbound:
            for tgt, _, _ in self._outbound[node_id]:
                in_degree[tgt] = in_degree.get(tgt, 0) + 1

        queue: deque[str] = deque(
            [node_id for node_id, deg in in_degree.items() if deg == 0]
        )
        result: List[Decision] = []

        while queue:
            node_id = queue.popleft()
            result.append(self._nodes[node_id])
            for tgt, _, _ in self._outbound.get(node_id, []):
                in_degree[tgt] -= 1
                if in_degree[tgt] == 0:
                    queue.append(tgt)

        if len(result) < len(self._nodes):
            remaining = [
                self._nodes[nid]
                for nid in self._nodes
                if self._nodes[nid] not in result
            ]
            logger.warning(
                "DecisionGraph.topological_sort: cycle detected — %d nodes remain",
                len(remaining),
            )
            result.extend(remaining)

        return result

    def find_path(
        self,
        source_id: str,
        target_id: str,
    ) -> List[Decision]:
        """
        DFS path from source to target.

        Returns the list of Decision nodes along the first found path,
        or an empty list if no path exists.
        """
        if source_id not in self._nodes or target_id not in self._nodes:
            return []

        visited: Set[str] = set()
        path: List[str] = []

        def dfs(current: str) -> bool:
            if current in visited:
                return False
            visited.add(current)
            path.append(current)
            if current == target_id:
                return True
            for tgt, _, _ in self._outbound.get(current, []):
                if dfs(tgt):
                    return True
            path.pop()
            return False

        dfs(source_id)
        return [self._nodes[nid] for nid in path]

    def get_neighbours(self, decision_id: str) -> List[Decision]:
        """Return all immediate successors (outbound neighbours) of a node."""
        return [
            self._nodes[tgt]
            for tgt, _, _ in self._outbound.get(decision_id, [])
            if tgt in self._nodes
        ]

    def get_predecessors(self, decision_id: str) -> List[Decision]:
        """Return all immediate predecessors (inbound neighbours) of a node."""
        return [
            self._nodes[src]
            for src, _, _ in self._inbound.get(decision_id, [])
            if src in self._nodes
        ]

    # ─────────────────────────────────────────────────────────────────────────
    #  Cycle detection
    # ─────────────────────────────────────────────────────────────────────────

    def detect_cycles(self) -> List[List[str]]:
        """
        Detect all strongly connected components of size > 1 using DFS.

        Returns a list of cycles, each cycle being a list of decision IDs.
        A non-empty return indicates circular decision dependencies.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        colour: Dict[str, int] = {nid: WHITE for nid in self._nodes}
        cycles: List[List[str]] = []
        stack: List[str] = []

        def dfs(node: str) -> None:
            colour[node] = GRAY
            stack.append(node)
            for tgt, _, _ in self._outbound.get(node, []):
                if colour[tgt] == GRAY:
                    # Found a back-edge → extract cycle
                    cycle_start = stack.index(tgt)
                    cycles.append(list(stack[cycle_start:]))
                elif colour[tgt] == WHITE:
                    dfs(tgt)
            stack.pop()
            colour[node] = BLACK

        for node_id in self._nodes:
            if colour[node_id] == WHITE:
                dfs(node_id)

        return cycles

    # ─────────────────────────────────────────────────────────────────────────
    #  Serialisation
    # ─────────────────────────────────────────────────────────────────────────

    def to_adjacency_dict(self) -> Dict[str, Any]:
        """
        Return a JSON-serialisable adjacency representation.

        Format::

            {
              "nodes": [{"id": "...", "name": "...", "type": "...", "status": "..."}],
              "edges": [{"source": "...", "target": "...", "type": "...", "confidence": 0.8}]
            }
        """
        nodes = [
            {
                "id": str(d.id),
                "name": d.name,
                "decision_type": d.decision_type.value,
                "status": d.status.value,
                "confidence": d.confidence.score,
            }
            for d in self._nodes.values()
        ]
        edges = []
        for src, neighbours in self._outbound.items():
            for tgt, rel, conf in neighbours:
                edges.append({
                    "source": src,
                    "target": tgt,
                    "relationship_type": rel,
                    "confidence": conf,
                })
        return {"nodes": nodes, "edges": edges}

    def to_networkx(self) -> Any:
        """
        Return a NetworkX DiGraph for external graph analysis.

        NetworkX is an optional dependency — if not installed, raises ImportError
        with a helpful message.
        """
        try:
            import networkx as nx  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "networkx is required for DecisionGraph.to_networkx(). "
                "Install it with: pip install networkx"
            ) from exc

        G = nx.DiGraph()
        for node_id, decision in self._nodes.items():
            G.add_node(
                node_id,
                name=decision.name,
                decision_type=decision.decision_type.value,
                status=decision.status.value,
                confidence=decision.confidence.score,
            )
        for src, neighbours in self._outbound.items():
            for tgt, rel, conf in neighbours:
                G.add_edge(src, tgt, relationship_type=rel, confidence=conf)

        return G
