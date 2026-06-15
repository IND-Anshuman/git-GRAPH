"""Overlap detection engine for capabilities."""

from typing import List, Dict, Any

class CapabilityOverlapEngine:
    """Detects duplicate and near-duplicate capabilities based on concept/behavior overlap."""

    def detect_overlaps(self, capabilities: List[Any]) -> List[Dict[str, Any]]:
        """
        Scans a list of capabilities and reports overlaps using Jaccard index on their concepts.
        Recommends 'MERGE' for overlap score >= 0.80, and 'REVIEW' for scores between 0.50 and 0.80.
        """
        overlaps = []
        for i in range(len(capabilities)):
            for j in range(i + 1, len(capabilities)):
                cap1 = capabilities[i]
                cap2 = capabilities[j]

                concepts1 = set(cap1.concepts)
                concepts2 = set(cap2.concepts)

                intersection = concepts1.intersection(concepts2)
                union = concepts1.union(concepts2)
                overlap_score = len(intersection) / len(union) if union else 0.0

                if overlap_score >= 0.5:
                    overlaps.append({
                        "capability_a_id": str(cap1.id),
                        "capability_a_name": cap1.name,
                        "capability_b_id": str(cap2.id),
                        "capability_b_name": cap2.name,
                        "overlap_score": round(overlap_score, 3),
                        "recommendation": "MERGE" if overlap_score >= 0.8 else "REVIEW"
                    })
        return overlaps
