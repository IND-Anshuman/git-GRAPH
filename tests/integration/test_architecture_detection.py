"""
Integration tests - Phase 7B: Architecture Detection Engine.
Tests the ArchitectureReasoningEngine and pattern detection.
"""
import pytest
import uuid
from datetime import datetime, timezone

from src.application.architecture.architecture_type import ArchitectureType
from src.application.architecture.architecture_graph import ArchitectureGraph, ArchitectureNode, ArchitectureEdge
from src.application.architecture.architecture_pattern_registry import ArchitecturePatternRegistry
from src.application.architecture.architecture_reasoning_engine import ArchitectureReasoningEngine

@pytest.fixture
def mock_architecture_graph():
    graph = ArchitectureGraph()
    # Mock layered architecture
    graph.add_node(ArchitectureNode(node_id="ui", node_type="Capability", label="UI Layer", metadata={"layer": "presentation"}))
    graph.add_node(ArchitectureNode(node_id="api", node_type="Capability", label="API Layer", metadata={"layer": "application"}))
    graph.add_node(ArchitectureNode(node_id="domain", node_type="Capability", label="Domain Layer", metadata={"layer": "domain"}))
    graph.add_node(ArchitectureNode(node_id="db", node_type="Capability", label="Database Layer", metadata={"layer": "infrastructure"}))
    
    graph.add_edge(ArchitectureEdge(from_id="ui", to_id="api", relationship="DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge(from_id="api", to_id="domain", relationship="DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge(from_id="domain", to_id="db", relationship="DEPENDS_ON"))
    
    return graph

def test_pattern_registry_loads_patterns():
    registry = ArchitecturePatternRegistry(patterns_dir="data/architecture_patterns")
    patterns = registry.get_all_patterns()
    assert isinstance(patterns, dict)
    # Registry should be able to load at least something (even if just empty list if no files)
    # or built-in patterns if provided.

def test_architecture_detection(mock_architecture_graph):
    engine = ArchitectureReasoningEngine(pattern_registry=ArchitecturePatternRegistry(patterns_dir="data/architecture_patterns"))
    profile = engine.detect_architecture("repo-1", "commit-1", mock_architecture_graph)
    
    assert profile is not None
    assert isinstance(profile.architecture_type, ArchitectureType)
    assert profile.repository_id == "repo-1"
    assert profile.commit_hash == "commit-1"
    
    # We expect some confidence score in [0.0, 1.0]
    assert 0.0 <= profile.confidence.score <= 1.0
    
    # Check that evidence is gathered
    assert isinstance(profile.evidence.capabilities, list)
    assert isinstance(profile.evidence.dependency_paths, list)

def test_empty_graph_detection():
    engine = ArchitectureReasoningEngine(pattern_registry=ArchitecturePatternRegistry(patterns_dir="data/architecture_patterns"))
    empty_graph = ArchitectureGraph()
    profile = engine.detect_architecture("repo-2", "commit-2", empty_graph)
    
    # An empty graph might yield UNKNOWN architecture type
    assert profile.architecture_type == ArchitectureType.UNKNOWN
    assert profile.confidence.score == 0.0
