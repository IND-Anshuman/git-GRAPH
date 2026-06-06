"""Unit tests for BehaviorDriftEngine."""

import uuid
from datetime import datetime
from src.domain.entities.logic_transition import LogicTransition
from src.domain.entities.logic_version import LogicVersion
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.domain.enums.transition_type import TransitionType
from src.domain.enums.drift_category import DriftCategory
from src.infrastructure.logic.behavior_drift_engine import BehaviorDriftEngine


def test_behavior_drift_calculation():
    engine = BehaviorDriftEngine()
    
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("x", "y", "c") # structural and dependency drift
    
    sig_id = uuid.uuid4()
    v1 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=uuid.uuid4(),
        commit_hash="hash1",
        version_ordinal=1,
        fingerprint=fp1,
        overall_confidence=0.90,
        metadata={"ontology_node_id": "security.authentication.direct_compare", "source_file": "file.py"},
        created_at=datetime.utcnow()
    )
    v2 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=v1.code_entity_seid,
        commit_hash="hash2",
        version_ordinal=2,
        fingerprint=fp2,
        overall_confidence=0.90,
        metadata={"ontology_node_id": "security.authentication.hash_comparison", "source_file": "file.py"},
        created_at=datetime.utcnow()
    )
    
    transition = LogicTransition(
        id=uuid.uuid4(),
        from_logic_version_id=v1.id,
        to_logic_version_id=v2.id,
        transition_type=TransitionType.EVOLVED,
        similarity_score=0.50,
        overall_confidence=0.90,
        created_at=datetime.utcnow()
    )
    
    drift = engine.compute_drift(transition, v1, v2)
    
    # structural drift: 0.60, dependency drift: 0.70
    # structural drift weight is 0.30, dependency drift weight is 0.25, security drift is 1.0 (boundary crossed)
    # let's verify overall drift calculation and category
    assert drift.drift_score > 0.0
    assert drift.ontology_changed
    assert drift.security_boundary_crossed
    assert drift.drift_category in [DriftCategory.SIGNIFICANT, DriftCategory.MAJOR, DriftCategory.COMPLETE]
