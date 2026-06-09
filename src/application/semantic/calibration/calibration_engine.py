"""Confidence Calibration Engine for centralized confidence formulas and calculations."""

import math
from typing import List, Tuple, Optional


class ConfidenceCalibrationEngine:
    """Centralized engine coordinating confidence scaling, Bayesian updates, and Noisy-OR aggregations."""

    @staticmethod
    def sigmoidal_scale(
        value: float,
        steepness: float = 10.0,
        midpoint: float = 0.5,
    ) -> float:
        """Scales a raw density or evidence count value using a sigmoid curve.

        Formula: f(x) = 1 / (1 + exp(-steepness * (value - midpoint)))
        """
        # Clamp value to [0, inf)
        val = max(0.0, value)
        try:
            return 1.0 / (1.0 + math.exp(-steepness * (val - midpoint)))
        except OverflowError:
            return 0.0 if (val - midpoint) < 0 else 1.0

    @staticmethod
    def update_bayesian_prior(
        prior: float,
        likelihood_positive: float = 0.8,
        likelihood_negative: float = 0.2,
        observed: bool = True,
    ) -> float:
        """Updates a prior confidence value given a new evidence observation.

        Posterior P(C|E) = P(E|C)P(C) / (P(E|C)P(C) + P(E|~C)P(~C))
        """
        # Ensure bounds
        prior = max(0.01, min(0.99, prior))
        
        if observed:
            # Positive evidence observed
            numerator = likelihood_positive * prior
            denominator = numerator + likelihood_negative * (1.0 - prior)
        else:
            # Positive evidence NOT observed (negative update)
            numerator = (1.0 - likelihood_positive) * prior
            denominator = numerator + (1.0 - likelihood_negative) * (1.0 - prior)

        if denominator == 0:
            return prior
        return max(0.0, min(1.0, numerator / denominator))

    @staticmethod
    def noisy_or_aggregate(
        scores: List[float],
        alpha: float = 0.5,
    ) -> float:
        """Aggregates multiple confidence scores using a decayed Noisy-OR formulation.

        Formula: 1.0 - Prod_i (1.0 - score_i * (alpha ** index))
        """
        if not scores:
            return 0.0
        
        # Sort descending to give higher weight to stronger evidence
        sorted_scores = sorted(scores, reverse=True)
        prod = 1.0
        for idx, score in enumerate(sorted_scores):
            # Clamp score to [0.0, 1.0]
            clamped = max(0.0, min(1.0, score))
            prod *= (1.0 - clamped * (alpha ** idx))
        
        return 1.0 - prod

    @staticmethod
    def taxonomically_decayed_noisy_or(
        evidence: List[Tuple[float, int]],  # List of (confidence_score, depth_or_distance)
        target_depth: int = 0,
        base_decay: float = 0.85,
    ) -> float:
        """Aggregates confidence scores with a decay based on taxonomic depth/distance.

        Formula: 1.0 - Prod_i (1.0 - score_i * (base_decay ** |depth_i - target_depth|))
        """
        if not evidence:
            return 0.0

        prod = 1.0
        for score, depth in evidence:
            distance = abs(depth - target_depth)
            decay = base_decay ** distance
            clamped_score = max(0.0, min(1.0, score))
            prod *= (1.0 - clamped_score * decay)

        return 1.0 - prod

    @classmethod
    def calibrate_joint_confidence(
        cls,
        evidence_scores: List[float],
        max_single_score: float,
        boost_limit: float = 0.25,
    ) -> float:
        """Calibrates joint confidence by capping it relative to the strongest single evidence.

        Ensures joint aggregation doesn't unrealistically boost low-confidence sets.
        """
        if not evidence_scores:
            return max(0.05, min(1.0, max_single_score))

        joint_conf = cls.noisy_or_aggregate(evidence_scores)
        # Cap logic: max_single + (1.0 - max_single) * boost_limit
        max_single = max(0.0, min(1.0, max_single_score))
        calibrated = min(joint_conf, max_single + (1.0 - max_single) * boost_limit)
        return max(0.05, min(1.0, calibrated))
