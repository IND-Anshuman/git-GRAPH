"""Unit tests for LogicFingerprint value object."""

import hashlib
from src.domain.value_objects.logic_fingerprint import LogicFingerprint


def test_logic_fingerprint_computation():
    struct = "struct_hash_123"
    dep = "dep_hash_123"
    beh = "beh_hash_123"
    
    fp = LogicFingerprint.compute(struct, dep, beh)
    
    expected_composite = hashlib.sha256((struct + dep + beh).encode('utf-8')).hexdigest()
    assert fp.structure_hash == struct
    assert fp.dependency_hash == dep
    assert fp.behavioral_hash == beh
    assert fp.composite == expected_composite
    assert fp.value == expected_composite


def test_logic_fingerprint_equality():
    fp1 = LogicFingerprint.compute("a", "b", "c")
    fp2 = LogicFingerprint.compute("a", "b", "c")
    fp3 = LogicFingerprint.compute("x", "y", "z")
    
    assert fp1 == fp2
    assert fp1 != fp3
    assert hash(fp1) == hash(fp2)
    assert hash(fp1) != hash(fp3)
