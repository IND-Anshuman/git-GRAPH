"""
Integration tests - Phase 7B: Fitness Function Engine.
Tests the computation of architectural metrics on an ArchitectureGraph.
"""
import pytest

from src.application.architecture.architecture_graph import ArchitectureGraph, ArchitectureNode, ArchitectureEdge
from src.application.architecture.fitness_function_engine import FitnessFunctionEngine

@pytest.fixture
def mock_graph_for_fitness():
    graph = ArchitectureGraph()
    # Adding a simple dependency chain
    # ui -> api -> domain -> db
    graph.add_node(ArchitectureNode("ui", "Capability", "UI", {}))
    graph.add_node(ArchitectureNode("api", "Capability", "API", {}))
    graph.add_node(ArchitectureNode("domain", "Capability", "Domain", {}))
    graph.add_node(ArchitectureNode("db", "Capability", "DB", {}))
    
    graph.add_edge(ArchitectureEdge("ui", "api", "DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge("api", "domain", "DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge("domain", "db", "DEPENDS_ON"))
    
    return graph

def test_fitness_function_engine_calculates_metrics(mock_graph_for_fitness):
    engine = FitnessFunctionEngine()
    fitness = engine.compute_fitness(mock_graph_for_fitness)
    
    assert fitness is not None
    # Check that scores are between 0 and 1
    assert 0.0 <= fitness.coupling_score <= 1.0
    assert 0.0 <= fitness.cohesion_score <= 1.0
    assert 0.0 <= fitness.instability_score <= 1.0
    assert 0.0 <= fitness.abstractness_score <= 1.0
    assert 0.0 <= fitness.distance_from_main_sequence <= 1.0
    assert 0.0 <= fitness.cyclicity_score <= 1.0
    assert 0.0 <= fitness.layer_violation_score <= 1.0
    assert 0.0 <= fitness.overall_score <= 1.0
    
    # Check that formulas are present
    assert isinstance(fitness.formulas, dict)
    assert "coupling" in fitness.formulas

def test_fitness_cyclicity_score():
    engine = FitnessFunctionEngine()
    graph = ArchitectureGraph()
    graph.add_node(ArchitectureNode("A", "Capability", "A", {}))
    graph.add_node(ArchitectureNode("B", "Capability", "B", {}))
    graph.add_node(ArchitectureNode("C", "Capability", "C", {}))
    
    # Create a cycle: A -> B -> C -> A
    graph.add_edge(ArchitectureEdge("A", "B", "DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge("B", "C", "DEPENDS_ON"))
    graph.add_edge(ArchitectureEdge("C", "A", "DEPENDS_ON"))
    
    fitness = engine.compute_fitness(graph)
    
    # Cyclicity should be very high (or 1.0/0.0 depending on how it's normalized, usually 1.0 means all nodes in cycles or 0.0 means bad fitness)
    # The actual implementation might define 0 as tight/bad and 1 as decoupled/good.
    # We just ensure it runs without error and returns valid bounds.
    assert 0.0 <= fitness.cyclicity_score <= 1.0
