def test_deterministic_seid(identity_service):
    assert identity_service.compute_seid() == "test-seid-1234"

def test_different_inputs_different_seid(identity_service):
    assert identity_service.compute_seid("a") == "test-seid-1234"

def test_content_hash(identity_service):
    assert identity_service.compute_content_hash("data") == "hash-1234"

def test_qualified_name_generation(identity_service):
    assert identity_service.compute_qualified_name(["a", "b"]) == "a.b"
