"""Python specific extraction strategy."""

from typing import Any, List, Dict, Optional
from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.infrastructure.extraction.strategies.base import IExtractionStrategy, RawEntity, RawRelationship

class PythonExtractionStrategy(IExtractionStrategy):
    """Strategy for extracting Python entities and relationships from tree-sitter AST."""
    
    def extract_entities(self, tree: Any, source_code: str, file_path: str, module_name: str) -> List[RawEntity]:
        entities = []
        source_bytes = source_code.encode("utf8")
        
        def walk(node: Any, parent_class: Optional[str] = None):
            if node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    entities.append(RawEntity(
                        name=name,
                        entity_type=EntityType.CLASS,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=source_bytes[node.start_byte:node.end_byte].decode("utf8")
                    ))
                    # walk children passing this class as parent
                    for child in node.children:
                        walk(child, parent_class=name)
            elif node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    ent_type = EntityType.METHOD if parent_class else EntityType.FUNCTION
                    entities.append(RawEntity(
                        name=name,
                        entity_type=ent_type,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=source_bytes[node.start_byte:node.end_byte].decode("utf8"),
                        parent_name=parent_class
                    ))
            elif node.type == "expression_statement":
                # Check for assignments for variables/constants
                for child in node.children:
                    if child.type == "assignment":
                        left = child.child_by_field_name("left")
                        if left and left.type == "identifier":
                            var_name = source_bytes[left.start_byte:left.end_byte].decode("utf8")
                            ent_type = EntityType.CONSTANT if var_name.isupper() else EntityType.VARIABLE
                            entities.append(RawEntity(
                                name=var_name,
                                entity_type=ent_type,
                                start_line=child.start_point[0] + 1,
                                end_line=child.end_point[0] + 1,
                                start_column=child.start_point[1] + 1,
                                end_column=child.end_point[1] + 1,
                                source_text=source_bytes[child.start_byte:child.end_byte].decode("utf8"),
                                parent_name=parent_class
                            ))
            else:
                for child in node.children:
                    walk(child, parent_class)
                    
        walk(tree.root_node)
        return entities
        
    def extract_relationships(self, tree: Any, source_code: str, entities: List[RawEntity]) -> List[RawRelationship]:
        relationships = []
        source_bytes = source_code.encode("utf8")
        
        # Build a simple name lookup
        entity_names = {e.name: e for e in entities}
        
        def walk(node: Any, current_scope: Optional[str] = None):
            scope = current_scope
            
            if node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    scope = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    
                # Base classes
                superclasses = node.child_by_field_name("superclasses")
                if superclasses and scope:
                    for child in superclasses.children:
                        if child.type == "identifier":
                            target = source_bytes[child.start_byte:child.end_byte].decode("utf8")
                            relationships.append(RawRelationship(
                                source_name=scope,
                                target_name=target,
                                relationship_type=RelationshipType.EXTENDS
                            ))
                            
            elif node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node:
                    scope = source_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    
            elif node.type == "call":
                func = node.child_by_field_name("function")
                if func and scope:
                    # Simplify: just grab the last identifier if it's an attribute
                    target = source_bytes[func.start_byte:func.end_byte].decode("utf8")
                    if "." in target:
                        target = target.split(".")[-1]
                    relationships.append(RawRelationship(
                        source_name=scope,
                        target_name=target,
                        relationship_type=RelationshipType.CALLS
                    ))
                    
            elif node.type in ("import_statement", "import_from_statement"):
                # Simplified import extraction
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    target = source_bytes[module_node.start_byte:module_node.end_byte].decode("utf8")
                    relationships.append(RawRelationship(
                        source_name="<module>",
                        target_name=target,
                        relationship_type=RelationshipType.IMPORTS
                    ))

            for child in node.children:
                walk(child, scope)
                
        walk(tree.root_node)
        
        # Also add BELONGS_TO relationships based on parents
        for entity in entities:
            if entity.parent_name:
                relationships.append(RawRelationship(
                    source_name=entity.name,
                    target_name=entity.parent_name,
                    relationship_type=RelationshipType.BELONGS_TO
                ))
                
        return relationships
