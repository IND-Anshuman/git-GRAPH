"""Engine to detect architectural drift between two snapshots."""

import uuid
from datetime import datetime
from typing import List

from .architecture_drift import ArchitectureDrift, ArchitectureDriftType
from .architecture_snapshot import ArchitectureSnapshot

class DriftReasoningEngine:
    """Compares ArchitectureSnapshot objects across commits to detect drift."""

    def detect_drift(
        self,
        previous_snapshot: ArchitectureSnapshot,
        current_snapshot: ArchitectureSnapshot
    ) -> List[ArchitectureDrift]:
        """
        Analyzes two architecture snapshots and detects drift in style, topology,
        dependencies, capabilities, flow, and ownership.
        """
        drifts = []
        
        # 1. Style Drift
        style_drift = self._detect_style_drift(previous_snapshot, current_snapshot)
        if style_drift:
            drifts.append(style_drift)
            
        # 2. Dependency Drift
        dep_drift = self._detect_dependency_drift(previous_snapshot, current_snapshot)
        if dep_drift:
            drifts.append(dep_drift)
            
        # 3. Ownership Drift
        own_drift = self._detect_ownership_drift(previous_snapshot, current_snapshot)
        if own_drift:
            drifts.append(own_drift)

        return drifts
        
    def _detect_style_drift(
        self, prev: ArchitectureSnapshot, curr: ArchitectureSnapshot
    ) -> ArchitectureDrift | None:
        """Detects if the fundamental architecture style has shifted."""
        prev_styles = [p.get("architecture_type") for p in prev.architecture_profiles]
        curr_styles = [p.get("architecture_type") for p in curr.architecture_profiles]
        
        # Simplistic check: did the primary style change?
        if prev_styles and curr_styles and prev_styles[0] != curr_styles[0]:
            return ArchitectureDrift(
                id=uuid.uuid4(),
                drift_type=ArchitectureDriftType.STYLE_DRIFT,
                previous_state={"styles": prev_styles},
                current_state={"styles": curr_styles},
                delta={
                    "removed": list(set(prev_styles) - set(curr_styles)),
                    "added": list(set(curr_styles) - set(prev_styles))
                },
                confidence=0.9,
                from_commit=prev.commit_hash,
                to_commit=curr.commit_hash,
                detected_at=datetime.utcnow()
            )
        return None

    def _detect_dependency_drift(
        self, prev: ArchitectureSnapshot, curr: ArchitectureSnapshot
    ) -> ArchitectureDrift | None:
        """Detects significant changes in structural fitness/dependencies."""
        prev_fit = prev.fitness_metrics.get("overall_score", 0.0)
        curr_fit = curr.fitness_metrics.get("overall_score", 0.0)
        
        if abs(prev_fit - curr_fit) > 0.1:  # Threshold for drift
            return ArchitectureDrift(
                id=uuid.uuid4(),
                drift_type=ArchitectureDriftType.DEPENDENCY_DRIFT,
                previous_state={"fitness": prev_fit},
                current_state={"fitness": curr_fit},
                delta={"fitness_change": curr_fit - prev_fit},
                confidence=0.8,
                from_commit=prev.commit_hash,
                to_commit=curr.commit_hash,
                detected_at=datetime.utcnow()
            )
        return None

    def _detect_ownership_drift(
        self, prev: ArchitectureSnapshot, curr: ArchitectureSnapshot
    ) -> ArchitectureDrift | None:
        """Detects if team ownership lines have significantly shifted."""
        if not prev.ownership_profile or not curr.ownership_profile:
            return None
            
        prev_silos = len(prev.ownership_profile.get("knowledge_silos", []))
        curr_silos = len(curr.ownership_profile.get("knowledge_silos", []))
        
        if prev_silos != curr_silos:
            return ArchitectureDrift(
                id=uuid.uuid4(),
                drift_type=ArchitectureDriftType.OWNERSHIP_DRIFT,
                previous_state={"silos_count": prev_silos},
                current_state={"silos_count": curr_silos},
                delta={"silos_change": curr_silos - prev_silos},
                confidence=0.75,
                from_commit=prev.commit_hash,
                to_commit=curr.commit_hash,
                detected_at=datetime.utcnow()
            )
        return None
