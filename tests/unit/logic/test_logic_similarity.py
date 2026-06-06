"""Unit tests for LogicSimilarityEngine."""

from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.infrastructure.logic.logic_similarity_engine import LogicSimilarityEngine


def test_logic_similarity_exact_match():
    engine = LogicSimilarityEngine()
    
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("a", "b", "c")
    
    similarity = engine.compute_similarity(fp1, fp2)
    assert similarity == 1.0


def test_logic_similarity_partial_match():
    engine = LogicSimilarityEngine()
    
    # Matching structure only: 0.40 * 1.0 + 0.35 * 0.0 + 0.25 * 0.0 = 0.40
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("a", "x", "y")
    assert abs(engine.compute_similarity(fp1, fp2) - 0.40) < 0.001
    
    # Matching dependency only: 0.35
    fp3 = LogicFingerprint.compute("a", "b", "c")
    fp4 = LogicFingerprint.compute("x", "b", "y")
    assert abs(engine.compute_similarity(fp3, fp4) - 0.35) < 0.001
    
    # Matching behavioral only: 0.25
    fp5 = LogicFingerprint.compute("a", "b", "c")
    fp6 = LogicFingerprint.compute("x", "y", "c")
    assert abs(engine.compute_similarity(fp5, fp6) - 0.25) < 0.001


def test_logic_similarity_no_match():
    engine = LogicSimilarityEngine()
    
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("x", "y", "z")
    
    similarity = engine.compute_similarity(fp1, fp2)
    assert similarity == 0.0
