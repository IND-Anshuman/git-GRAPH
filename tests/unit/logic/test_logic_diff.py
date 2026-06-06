"""Unit tests for LogicDiffEngine."""

import uuid
from datetime import datetime
from src.domain.entities.logic_version import LogicVersion
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.infrastructure.logic.logic_diff_engine import LogicDiffEngine


def test_logic_diff_no_changes():
    engine = LogicDiffEngine()
    
    fp = LogicFingerprint.compute("a", "b", "c")
    sig_id = uuid.uuid4()
    
    v1 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=uuid.uuid4(),
        commit_hash="hash1",
        version_ordinal=1,
        fingerprint=fp,
        overall_confidence=0.90,
        metadata={"source_file": "file.py"},
        created_at=datetime.utcnow()
    )
    v2 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=v1.code_entity_seid,
        commit_hash="hash2",
        version_ordinal=2,
        fingerprint=fp,
        overall_confidence=0.90,
        metadata={"source_file": "file.py"},
        created_at=datetime.utcnow()
    )
    
    diff = engine.diff_versions(v1, v2)
    assert not diff["has_changes"]
    assert not diff["structural_changed"]
    assert not diff["dependency_changed"]
    assert not diff["behavioral_changed"]
    assert diff["confidence_drift"] == 0.0


def test_logic_diff_with_changes():
    engine = LogicDiffEngine()
    
    sig_id = uuid.uuid4()
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("x", "b", "y") # structure and behavioral changed
    
    v1 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=uuid.uuid4(),
        commit_hash="hash1",
        version_ordinal=1,
        fingerprint=fp1,
        overall_confidence=0.90,
        metadata={"source_file": "file.py"},
        created_at=datetime.utcnow()
    )
    v2 = LogicVersion(
        id=uuid.uuid4(),
        logic_signature_id=sig_id,
        code_entity_seid=v1.code_entity_seid,
        commit_hash="hash2",
        version_ordinal=2,
        fingerprint=fp2,
        overall_confidence=0.85,
        metadata={"source_file": "file_new.py"},
        created_at=datetime.utcnow()
    )
    
    diff = engine.diff_versions(v1, v2)
    assert diff["has_changes"]
    assert diff["structural_changed"]
    assert not diff["dependency_changed"]
    assert diff["behavioral_changed"]
    assert abs(diff["confidence_drift"] - (-0.05)) < 0.001
    assert "structural" in diff["summary"]
    assert "behavioral" in diff["summary"]
    assert diff["metadata_diff"]["from_file"] == "file.py"
    assert diff["metadata_diff"]["to_file"] == "file_new.py"
