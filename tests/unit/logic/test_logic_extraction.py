"""Unit tests for LogicExtractionEngine."""

import uuid
from unittest.mock import MagicMock
from src.domain.entities.code_entity import CodeEntity
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.domain.enums.entity_type import EntityType
from src.domain.enums.language import SupportedLanguage
from src.domain.value_objects.entity_id import SEID
from src.domain.value_objects.file_id import FileId
from src.domain.value_objects.repository_id import RepositoryId
from src.domain.value_objects.code_location import CodeLocation
from src.application.ports.ast_feature_port import ASTFeatures, ExtractedFeature
from src.domain.value_objects.logic_fingerprint import LogicFingerprint
from src.infrastructure.logic.logic_extraction_engine import LogicExtractionEngine


def test_extract_logic_successful_match():
    # Arrange
    extractor = MagicMock()
    fingerprinter = MagicMock()
    registry = MagicMock()
    
    engine = LogicExtractionEngine(extractor, fingerprinter, registry)
    
    repo_id = RepositoryId.generate()
    entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.FUNCTION,
        name="verify_credentials",
        qualified_name="auth.verify_credentials",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/auth.py", 10, 20, 0, 0)
    )
    
    features = ASTFeatures(
        calls=[
            ExtractedFeature(feature_type="call", symbol="call:bcrypt.checkpw", line_number=15),
        ],
        imports=[
            ExtractedFeature(feature_type="import", symbol="import:bcrypt", line_number=1),
        ],
        data_flows=[
            {
                "source": "provided_password",
                "sink": "bcrypt.checkpw",
                "line": 15,
                "path": ["provided_password", "checkpw"]
            }
        ]
    )
    extractor.extract_features.return_value = features
    
    fingerprint = LogicFingerprint.compute("struct_hash", "dep_hash", "beh_hash")
    fingerprinter.compute_fingerprint.return_value = fingerprint
    
    pattern = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="auth_bcrypt_verification",
        name="Bcrypt Verification",
        ontology_node_id="security.authentication.hash_comparison",
        base_confidence=0.95,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={
            "negative_indicators": [{"symbol": "direct_compare"}],
            "ast_features": [
                {"match_type": "call", "target_function": "checkpw", "target_module": "bcrypt", "description": "bcrypt checkpw"},
                {"match_type": "import", "target_module": "bcrypt", "description": "import bcrypt"}
            ],
            "data_flow": [
                {"source_param_pattern": "password", "sink_call": "bcrypt.checkpw"}
            ],
            "required_params": [
                {"name_pattern": "password"}
            ]
        },
        index_keys=["call:bcrypt.checkpw", "import:bcrypt"],
        is_active=True
    )
    registry.get_candidate_patterns.return_value = [pattern]
    
    # Act
    results = engine.extract_logic(entity, MagicMock(), "source_code", "commit_123")
    
    # Assert
    assert len(results) == 1
    sig, ver, evs, exp = results[0]
    
    assert sig.canonical_name == "auth_bcrypt_verification"
    assert sig.ontology_node_id == "security.authentication.hash_comparison"
    assert ver.commit_hash == "commit_123"
    assert ver.fingerprint == fingerprint
    assert ver.overall_confidence > 0.80
    assert len(evs) == 3 # call, import, and data flow
    assert exp.behavior_name == "Bcrypt Verification"


def test_extract_logic_negative_indicator_disqualifies():
    # Arrange
    extractor = MagicMock()
    fingerprinter = MagicMock()
    registry = MagicMock()
    
    engine = LogicExtractionEngine(extractor, fingerprinter, registry)
    
    repo_id = RepositoryId.generate()
    entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.FUNCTION,
        name="verify_credentials",
        qualified_name="auth.verify_credentials",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/auth.py", 10, 20, 0, 0)
    )
    
    features = ASTFeatures(
        calls=[
            ExtractedFeature(feature_type="call", symbol="call:bcrypt.checkpw", line_number=15),
            ExtractedFeature(feature_type="call", symbol="call:direct_compare", line_number=16),
        ],
        imports=[
            ExtractedFeature(feature_type="import", symbol="import:bcrypt", line_number=1),
        ]
    )
    extractor.extract_features.return_value = features
    
    fingerprint = LogicFingerprint.compute("struct_hash", "dep_hash", "beh_hash")
    fingerprinter.compute_fingerprint.return_value = fingerprint
    
    pattern = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="auth_bcrypt_verification",
        name="Bcrypt Verification",
        ontology_node_id="security.authentication.hash_comparison",
        base_confidence=0.95,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={
            "negative_indicators": [{"symbol": "direct_compare"}],
            "ast_features": [
                {"match_type": "call", "target_function": "checkpw", "target_module": "bcrypt", "description": "bcrypt checkpw"}
            ]
        },
        index_keys=["call:bcrypt.checkpw", "import:bcrypt"],
        is_active=True
    )
    registry.get_candidate_patterns.return_value = [pattern]
    
    # Act
    results = engine.extract_logic(entity, MagicMock(), "source_code", "commit_123")
    
    # Assert
    assert len(results) == 0 # Disqualified due to negative indicator


def test_extract_logic_subscript_cache_match():
    # Arrange
    extractor = MagicMock()
    fingerprinter = MagicMock()
    registry = MagicMock()
    
    engine = LogicExtractionEngine(extractor, fingerprinter, registry)
    
    repo_id = RepositoryId.generate()
    entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.FUNCTION,
        name="get_cached_user",
        qualified_name="auth.get_cached_user",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/auth.py", 10, 20, 0, 0)
    )
    
    features = ASTFeatures(
        subscripts=[
            ExtractedFeature(feature_type="subscript", symbol="struct:subscript", line_number=15, metadata={"raw": "user_cache[id]"}),
        ]
    )
    extractor.extract_features.return_value = features
    
    fingerprint = LogicFingerprint.compute("struct_hash", "dep_hash", "beh_hash")
    fingerprinter.compute_fingerprint.return_value = fingerprint
    
    pattern = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="cache_memory_dict",
        name="In-Memory Dictionary Cache",
        ontology_node_id="data_management.caching.memory",
        base_confidence=0.78,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={
            "ast_features": [
                {"match_type": "subscript", "key_pattern": "(\\b_?cache|\\bcache_\\w*|\\b\\w*_cache)\\["}
            ]
        },
        index_keys=["struct:dict_lookup"],
        is_active=True
    )
    registry.get_candidate_patterns.return_value = [pattern]
    
    # Act
    results = engine.extract_logic(entity, MagicMock(), "source_code", "commit_123")
    
    # Assert
    assert len(results) == 1
    sig, ver, evs, exp = results[0]
    assert sig.canonical_name == "cache_memory_dict"
    assert len(evs) == 1
    assert evs[0].ast_node_type == "Subscript"


def test_extract_logic_gql_query_negative_indicator_string():
    # Arrange
    extractor = MagicMock()
    fingerprinter = MagicMock()
    registry = MagicMock()
    
    engine = LogicExtractionEngine(extractor, fingerprinter, registry)
    
    repo_id = RepositoryId.generate()
    entity = CodeEntity(
        seid=SEID.generate(),
        entity_type=EntityType.FUNCTION,
        name="run_gql",
        qualified_name="api.run_gql",
        file_id=FileId(uuid.uuid4()),
        repository_id=repo_id,
        parent_seid=None,
        language=SupportedLanguage.PYTHON,
        location=CodeLocation("src/api.py", 10, 20, 0, 0)
    )
    
    features = ASTFeatures(
        calls=[
            ExtractedFeature(feature_type="call", symbol="call:execute", line_number=15),
        ],
        imports=[
            ExtractedFeature(feature_type="import", symbol="import:gql", line_number=1),
        ],
        strings=[
            ExtractedFeature(feature_type="string", symbol="string:literal", line_number=15, metadata={"raw": "mutation update { ... }"}),
        ]
    )
    extractor.extract_features.return_value = features
    
    fingerprint = LogicFingerprint.compute("struct_hash", "dep_hash", "beh_hash")
    fingerprinter.compute_fingerprint.return_value = fingerprint
    
    # GQL Query has negative indicator "mutation"
    query_pattern = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="gql_query",
        name="GraphQL Client Query",
        ontology_node_id="integration.http_client.graphql_call",
        base_confidence=0.93,
        pattern_version="1.0.0",
        schema_version="1.0",
        rules={
            "ast_features": [
                {"match_type": "call", "target_method": "execute"},
                {"match_type": "import", "target_module": "gql"}
            ],
            "negative_indicators": [{"symbol": "mutation"}]
        },
        index_keys=["call:execute", "import:gql"],
        is_active=True
    )
    registry.get_candidate_patterns.return_value = [query_pattern]
    
    # Act
    results = engine.extract_logic(entity, MagicMock(), "source_code", "commit_123")
    
    # Assert
    assert len(results) == 0 # Disqualified because the string contains "mutation"
