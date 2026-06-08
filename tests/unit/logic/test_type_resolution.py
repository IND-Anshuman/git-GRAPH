"""Unit tests for generic type resolution and normalization."""

from src.application.semantic.type_resolution.type_resolution_engine import TypeResolutionEngine
from src.application.semantic.type_resolution.generic_normalizer import GenericNormalizer


def test_generic_normalizer_strip():
    """Verify that GenericNormalizer correctly strips interfaces and extracts generics."""
    # Test cases: (input, expected_base, expected_generics)
    cases = [
        ("IRepository<User>", "Repository", ["User"]),
        ("Repository<User>", "Repository", ["User"]),
        ("IUserService", "UserService", []),
        ("UserRepository", "UserRepository", []),
        ("IMap<String, Integer>", "Map", ["String", "Integer"]),
        ("", "", []),
    ]
    for inp, exp_base, exp_gen in cases:
        base, gen = GenericNormalizer.strip_generic_wrappers(inp)
        assert base == exp_base
        assert gen == exp_gen


def test_type_resolution_engine_resolve():
    """Verify TypeResolutionEngine resolve_type logic."""
    engine = TypeResolutionEngine()
    res = engine.resolve_type("IRepository<User>")
    assert res["original"] == "IRepository<User>"
    assert res["normalized_base"] == "Repository"
    assert res["generic_args"] == ["User"]
    assert res["is_generic"] is True

    res_simple = engine.resolve_type("UserService")
    assert res_simple["original"] == "UserService"
    assert res_simple["normalized_base"] == "UserService"
    assert res_simple["generic_args"] == []
    assert res_simple["is_generic"] is False


def test_type_resolution_engine_bind_methods():
    """Verify TypeResolutionEngine bind_interface_methods mapping."""
    engine = TypeResolutionEngine()
    methods = [
        {"name": "Save", "return_type": "Task<User>"},
        {"name": "Get", "return_type": "IUserService"},
    ]
    bound = engine.bind_interface_methods(
        class_name="UserRepository",
        interfaces=["IRepository<User>"],
        methods=methods
    )
    assert len(bound) == 2
    assert bound[0]["name"] == "Save"
    assert bound[0]["resolved_return_type"]["normalized_base"] == "Task"
    assert bound[0]["resolved_return_type"]["generic_args"] == ["User"]

    assert bound[1]["name"] == "Get"
    assert bound[1]["resolved_return_type"]["normalized_base"] == "UserService"
    assert bound[1]["resolved_return_type"]["generic_args"] == []
