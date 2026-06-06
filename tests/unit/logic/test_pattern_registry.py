"""Unit tests for PatternRegistry infrastructure service."""

import uuid
from datetime import datetime
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.infrastructure.logic.pattern_registry import PatternRegistry


def test_pattern_registry_registration_and_retrieval():
    registry = PatternRegistry()
    
    p1 = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="auth_bcrypt",
        name="Bcrypt Auth",
        ontology_node_id="security.authentication.hash_comparison",
        base_confidence=0.95,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={"call": "bcrypt.checkpw"},
        index_keys=["call:bcrypt.checkpw", "import:bcrypt"],
        is_active=True,
        loaded_at=datetime.utcnow()
    )
    
    p2 = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="auth_sha256",
        name="SHA-256 Auth",
        ontology_node_id="security.authentication.hash_comparison",
        base_confidence=0.85,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={"call": "hashlib.sha256"},
        index_keys=["call:hashlib.sha256", "import:hashlib"],
        is_active=True,
        loaded_at=datetime.utcnow()
    )
    
    registry.register_patterns([p1, p2])
    
    assert registry.get_by_pattern_id("auth_bcrypt") == p1
    assert registry.get_by_pattern_id("auth_sha256") == p2
    assert len(registry.get_all_patterns()) == 2
    
    # Get candidates
    candidates = registry.get_candidate_patterns(["call:bcrypt.checkpw"])
    assert p1 in candidates
    assert p2 not in candidates
    
    candidates_multiple = registry.get_candidate_patterns(["import:bcrypt", "import:hashlib"])
    assert p1 in candidates_multiple
    assert p2 in candidates_multiple
    
    # Clear
    registry.clear()
    assert len(registry.get_all_patterns()) == 0
    assert len(registry.get_candidate_patterns(["import:bcrypt"])) == 0
