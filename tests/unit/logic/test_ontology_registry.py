"""Unit tests for OntologyRegistryService."""

import uuid
from unittest.mock import MagicMock
from src.domain.entities.ontology_node import OntologyNode
from src.domain.entities.behavior_pattern import BehaviorPattern
from src.application.services.ontology_registry import OntologyRegistryService


def test_ontology_registry_queries():
    uow = MagicMock()
    uow_factory = lambda: uow
    loader = MagicMock()
    in_memory = MagicMock()
    
    service = OntologyRegistryService(uow_factory, loader, in_memory)
    
    # Mock behavior of Unit of Work context manager
    uow.__enter__.return_value = uow
    
    node = OntologyNode(
        id="security.authentication",
        name="Auth",
        parent_id=None,
        domain="Security",
        description="Authentication mechanisms",
        ontology_version="1.0"
    )
    uow.ontology_nodes.list_all.return_value = [node]
    uow.ontology_nodes.get_by_id.return_value = node
    
    pattern = BehaviorPattern(
        id=uuid.uuid4(),
        pattern_id="auth_bcrypt",
        name="Bcrypt",
        ontology_node_id="security.authentication.hash_comparison",
        base_confidence=0.95,
        pattern_version="1.0",
        schema_version="1.0",
        rules={}
    )
    uow.behavior_patterns.list_active.return_value = [pattern]
    uow.behavior_patterns.get_by_pattern_id.return_value = pattern
    
    assert service.get_all_nodes() == [node]
    assert service.get_node_by_id("security.authentication") == node
    
    assert service.get_all_patterns() == [pattern]
    assert service.get_pattern_by_id("auth_bcrypt") == pattern
