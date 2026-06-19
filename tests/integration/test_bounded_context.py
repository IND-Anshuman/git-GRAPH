"""
Integration tests - Phase 7B: Bounded Context Engine.
Tests the extraction of bounded contexts from an ArchitectureGraph.
"""
import pytest
from src.application.architecture.architecture_graph import ArchitectureGraph, ArchitectureNode, ArchitectureEdge
from src.application.architecture.bounded_context_engine import BoundedContextEngine

@pytest.fixture
def mock_graph_for_contexts():
    graph = ArchitectureGraph()
    # A graph with 2 distinct clusters
    # Cluster 1 (Sales)
    graph.add_node(ArchitectureNode("sales_api", "Capability", "Sales API", {"domain": "sales"}))
    graph.add_node(ArchitectureNode("sales_db", "Capability", "Sales DB", {"domain": "sales"}))
    graph.add_edge(ArchitectureEdge("sales_api", "sales_db", "DEPENDS_ON"))
    
    # Cluster 2 (Inventory)
    graph.add_node(ArchitectureNode("inventory_api", "Capability", "Inventory API", {"domain": "inventory"}))
    graph.add_node(ArchitectureNode("inventory_db", "Capability", "Inventory DB", {"domain": "inventory"}))
    graph.add_edge(ArchitectureEdge("inventory_api", "inventory_db", "DEPENDS_ON"))
    
    # One cross-context edge
    graph.add_edge(ArchitectureEdge("sales_api", "inventory_api", "DEPENDS_ON"))
    
    return graph

def test_bounded_context_engine_extracts_contexts(mock_graph_for_contexts):
    engine = BoundedContextEngine()
    
    # The engine should modify the graph to add BoundedContext nodes and CONTAINS edges,
    # or return a list of extracted contexts.
    engine.identify_contexts(mock_graph_for_contexts)
    
    # After identifying contexts, the graph should contain BoundedContext nodes
    context_nodes = [n for n in mock_graph_for_contexts.nodes.values() if n.node_type == "BoundedContext"]
    
    assert len(context_nodes) > 0
    
    for context in context_nodes:
        assert context.node_id is not None
        assert context.label is not None
        assert context.metadata.get("domain") is not None

def test_bounded_context_engine_empty_graph():
    engine = BoundedContextEngine()
    graph = ArchitectureGraph()
    engine.identify_contexts(graph)
    context_nodes = [n for n in graph.nodes.values() if n.node_type == "BoundedContext"]
    assert len(context_nodes) == 0

