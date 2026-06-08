"""Unit tests for semantic normalization and behavior mapping."""

import pytest
from src.application.semantic.isr import CanonicalEntity
from src.application.semantic.behavior_registry.canonical_registry import CanonicalRegistry
from src.application.semantic.normalization.semantic_normalizer import SemanticNormalizer
from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine


@pytest.fixture
def normalizer():
    registry = CanonicalRegistry()
    type_engine = TypeResolutionEngine()
    return SemanticNormalizer(registry, type_engine)


def test_normalize_entity(normalizer):
    """Verify that raw AST entity metadata is correctly mapped to a CanonicalEntity."""
    raw = {
        "name": "VerifyHashedPassword",
        "qualified_name": "AuthService.VerifyHashedPassword",
        "type": "Method",
        "visibility": "public",
        "return_type": "Task<bool>",
        "decorators": ["HttpPost"],
        "metadata": {"line": 42}
    }
    entity = normalizer.normalize_entity(raw, "csharp")
    assert entity.name == "VerifyHashedPassword"
    assert entity.qualified_name == "AuthService.VerifyHashedPassword"
    assert entity.entity_type == "Method"
    assert entity.visibility == "public"
    assert entity.return_type == "Task"
    assert entity.generics == ["bool"]
    assert entity.decorators == ["HttpPost"]
    assert entity.metadata == {"line": 42}


def test_map_behavior_python(normalizer):
    """Verify mapping python bcrypt calls to auth_password_verification."""
    entity = CanonicalEntity(
        id="test-py-id",
        name="check_credentials",
        qualified_name="auth.check_credentials",
        entity_type="Method"
    )
    behavior = normalizer.map_behavior(
        entity=entity,
        imports=["bcrypt", "os"],
        calls=["bcrypt.checkpw"],
        language="python"
    )
    assert behavior is not None
    assert behavior.canonical_id == "auth_password_verification"
    assert behavior.confidence == 1.0
    assert "bcrypt" in behavior.evidence.matched_imports
    assert "bcrypt.checkpw" in behavior.evidence.matched_calls


def test_map_behavior_java(normalizer):
    """Verify mapping Java Spring PasswordEncoder to auth_password_verification."""
    entity = CanonicalEntity(
        id="test-java-id",
        name="authenticate",
        qualified_name="com.app.service.AuthService.authenticate",
        entity_type="Method"
    )
    behavior = normalizer.map_behavior(
        entity=entity,
        imports=["org.springframework.security.crypto.password.PasswordEncoder"],
        calls=["PasswordEncoder.matches"],
        language="java"
    )
    assert behavior is not None
    assert behavior.canonical_id == "auth_password_verification"
    assert behavior.confidence == 1.0


def test_map_behavior_csharp(normalizer):
    """Verify mapping C# PasswordHasher to auth_password_verification."""
    entity = CanonicalEntity(
        id="test-cs-id",
        name="VerifyPassword",
        qualified_name="AuthService.VerifyPassword",
        entity_type="Method"
    )
    behavior = normalizer.map_behavior(
        entity=entity,
        imports=["Microsoft.AspNetCore.Identity.PasswordHasher"],
        calls=["PasswordHasher.VerifyHashedPassword"],
        language="csharp"
    )
    assert behavior is not None
    assert behavior.canonical_id == "auth_password_verification"
    assert behavior.confidence == 1.0


def test_map_behavior_rust(normalizer):
    """Verify mapping Rust argon2 to auth_password_verification."""
    entity = CanonicalEntity(
        id="test-rs-id",
        name="verify_pw",
        qualified_name="auth::verify_pw",
        entity_type="Method"
    )
    behavior = normalizer.map_behavior(
        entity=entity,
        imports=["argon2"],
        calls=["argon2.verify"],
        language="rust"
    )
    assert behavior is not None
    assert behavior.canonical_id == "auth_password_verification"
    assert behavior.confidence == 1.0


def test_map_behavior_heuristic_fallback(normalizer):
    """Verify that naming heuristic fallback triggers with lower confidence when imports/calls mismatch."""
    entity = CanonicalEntity(
        id="test-heuristic-id",
        name="VerifyPassword",
        qualified_name="AuthService.VerifyPassword",
        entity_type="Method"
    )
    # No relevant imports or calls
    behavior = normalizer.map_behavior(
        entity=entity,
        imports=[],
        calls=[],
        language="typescript"
    )
    assert behavior is not None
    assert behavior.canonical_id == "auth_password_verification"
    assert behavior.confidence == 0.70
    assert behavior.evidence.matched_heuristics.get("entity_name_match") is True
