"""Engine to generate the evolution sequence of architectural state over time."""

import uuid
from datetime import datetime
from typing import List

from .architecture_snapshot import ArchitectureSnapshot
from .architecture_timeline import ArchitectureTimeline, ArchitectureTimelineEntry
from .architecture_type import ArchitectureType

class ArchitectureTimelineEngine:
    """Generates an evolution sequence of architectural state over time."""

    def generate_timeline(
        self,
        repository_id: str,
        snapshots: List[ArchitectureSnapshot]
    ) -> ArchitectureTimeline:
        """
        Creates an ArchitectureTimeline from a chronological sequence of ArchitectureSnapshots.
        """
        # Sort snapshots by their generated_at timestamp just in case
        sorted_snapshots = sorted(snapshots, key=lambda s: s.generated_at)
        
        entries = []
        for i, snapshot in enumerate(sorted_snapshots):
            # Determine architecture type from profiles
            arch_type = ArchitectureType.UNKNOWN
            if snapshot.architecture_profiles:
                # Assuming profiles are dicts here as per snapshot schema
                profile = snapshot.architecture_profiles[0]
                arch_type_str = profile.get("architecture_type", "UNKNOWN")
                try:
                    if isinstance(arch_type_str, str):
                        arch_type = ArchitectureType(arch_type_str)
                    else:
                        arch_type = arch_type_str
                except ValueError:
                    arch_type = ArchitectureType.UNKNOWN
                    
            # Extract fitness score
            fitness_score = snapshot.fitness_metrics.get("overall_score", 0.0)
            
            # Determine key changes compared to previous snapshot
            key_changes = []
            if i > 0:
                prev = sorted_snapshots[i-1]
                prev_fit = prev.fitness_metrics.get("overall_score", 0.0)
                if abs(fitness_score - prev_fit) > 0.05:
                    key_changes.append(f"Fitness changed from {prev_fit:.2f} to {fitness_score:.2f}")
                    
                prev_silos = len(prev.ownership_profile.get("knowledge_silos", []))
                curr_silos = len(snapshot.ownership_profile.get("knowledge_silos", []))
                if prev_silos != curr_silos:
                    key_changes.append(f"Knowledge silos count changed from {prev_silos} to {curr_silos}")
            else:
                key_changes.append("Initial snapshot")
                
            entries.append(ArchitectureTimelineEntry(
                commit_hash=snapshot.commit_hash,
                architecture_type=arch_type,
                key_changes=key_changes,
                fitness_score=fitness_score,
                timestamp=snapshot.generated_at
            ))
            
        return ArchitectureTimeline(
            id=uuid.uuid4(),
            repository_id=repository_id,
            entries=entries,
            generated_at=datetime.utcnow()
        )
