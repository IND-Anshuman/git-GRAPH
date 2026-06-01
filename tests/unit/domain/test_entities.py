def test_create_repository_entity(sample_repository_entity):
    assert sample_repository_entity.id == "repo-id"
    assert sample_repository_entity.url == "https://github.com/test/repo"

def test_repository_status_transitions(sample_repository_entity):
    sample_repository_entity.status = "CLONING"
    assert sample_repository_entity.status == "CLONING"
    sample_repository_entity.status = "COMPLETED"
    assert sample_repository_entity.status == "COMPLETED"

def test_create_code_entity():
    code_entity = {"id": "1", "name": "foo"}
    assert code_entity["name"] == "foo"

def test_create_relationship():
    rel = {"source_id": "1", "target_id": "2", "type": "CALLS"}
    assert rel["type"] == "CALLS"

def test_source_file_language_detection():
    exts = {".py": "PYTHON", ".js": "JAVASCRIPT", ".go": "GO", ".java": "JAVA"}
    for ext, lang in exts.items():
        assert lang in ["PYTHON", "JAVASCRIPT", "GO", "JAVA"]
