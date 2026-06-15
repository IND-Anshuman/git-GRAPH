"""Taxonomy learning engine for resolving new categories and capability promotions."""

from typing import List, Dict, Any

class TaxonomyLearningEngine:
    """Discovers recurring patterns in capabilities to suggest promotions, new taxonomy categories, and archetypes."""

    def identify_taxonomy_candidates(self, capabilities: List[Any]) -> List[Dict[str, Any]]:
        """
        Scans active capabilities to identify new structural categories (e.g. Payment Systems, Observability Platforms).
        """
        candidates = []
        for cap in capabilities:
            name_lower = cap.name.lower()
            if "payment" in name_lower or "stripe" in name_lower or "paypal" in name_lower:
                candidates.append({
                    "suggested_category": "Payment Processing",
                    "reason": f"Heuristics matched capability: {cap.name}",
                    "confidence": 0.90
                })
            elif "auth" in name_lower or "jwt" in name_lower or "identity" in name_lower:
                candidates.append({
                    "suggested_category": "Identity & Access Management",
                    "reason": f"Heuristics matched capability: {cap.name}",
                    "confidence": 0.95
                })
            elif "retrieval" in name_lower or "agent" in name_lower or "memory" in name_lower:
                candidates.append({
                    "suggested_category": "AI & Agent Integration",
                    "reason": f"Heuristics matched capability: {cap.name}",
                    "confidence": 0.85
                })
        return candidates
