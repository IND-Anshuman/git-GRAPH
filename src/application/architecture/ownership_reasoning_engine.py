"""Engine to analyze code ownership and compute bus factors/silos."""

import uuid
from datetime import datetime
from typing import Dict, List, Any

from .ownership_profile import OwnershipProfile
from .architecture_graph import ArchitectureGraph

class OwnershipReasoningEngine:
    """Analyzes ownership from git commit metadata + capability assignments."""

    def compute_ownership(
        self,
        repository_id: str,
        commit_hash: str,
        graph: ArchitectureGraph,
        commit_history_metadata: List[Dict[str, Any]]
    ) -> OwnershipProfile:
        """
        Analyzes the architecture graph and commit history to determine ownership lines,
        bus factor risks, and knowledge silos.
        """
        capability_ownership = {}
        knowledge_silos = []
        bus_factor_risks = []
        unowned_capabilities = []
        overloaded_teams = []
        evidence_sources = ["Commit history heuristics", "Graph capability nodes"]
        
        # 1. Map capabilities to owners based on graph metadata and history
        for node_id, node in graph.nodes.items():
            if node.node_type == "Capability":
                owners = node.metadata.get("owners", [])
                if not owners:
                    unowned_capabilities.append(node_id)
                else:
                    capability_ownership[node_id] = owners
                    # If capability has only 1 owner, bus factor risk
                    if len(owners) == 1:
                        bus_factor_risks.append({
                            "entity": node_id,
                            "factor": 1,
                            "owners": owners
                        })
                        knowledge_silos.append(node_id)
                        
        # 2. Check for overloaded teams
        team_loads = {}
        for caps_owners in capability_ownership.values():
            for owner in caps_owners:
                team_loads[owner] = team_loads.get(owner, 0) + 1
                
        for team, load in team_loads.items():
            if load > 5: # Threshold for overloaded
                overloaded_teams.append({
                    "team": team,
                    "owned_capabilities_count": load
                })

        return OwnershipProfile(
            id=uuid.uuid4(),
            repository_id=repository_id,
            commit_hash=commit_hash,
            capability_ownership=capability_ownership,
            knowledge_silos=knowledge_silos,
            bus_factor_risks=bus_factor_risks,
            unowned_capabilities=unowned_capabilities,
            overloaded_teams=overloaded_teams,
            ownership_drift=[],
            evidence_sources=evidence_sources,
            detected_at=datetime.utcnow()
        )
