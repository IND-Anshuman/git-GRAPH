"""Shared extraction strategy for JavaScript, TypeScript, Go, and Java."""

from typing import Any, List, Optional

from src.domain.enums.entity_type import EntityType
from src.domain.enums.relationship_type import RelationshipType
from src.infrastructure.extraction.strategies.base import (
    IExtractionStrategy,
    RawEntity,
    RawRelationship,
)


class Wave1ExtractionStrategy(IExtractionStrategy):
    """Broad structural extractor for first-wave multi-language support."""

    def __init__(self, language_key: str) -> None:
        self.language_key = language_key

    def extract_entities(
        self, tree: Any, source_code: str, file_path: str, module_name: str
    ) -> List[RawEntity]:
        if tree is None or getattr(tree, "root_node", None) is None:
            return []

        entities: List[RawEntity] = []
        source_bytes = source_code.encode("utf8")

        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")

        def make_entity(
            node: Any,
            name_node: Any,
            entity_type: EntityType,
            parent_name: Optional[str] = None,
        ) -> None:
            if not name_node:
                return
            entities.append(
                RawEntity(
                    name=text(name_node),
                    entity_type=entity_type,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    start_column=node.start_point[1] + 1,
                    end_column=node.end_point[1] + 1,
                    source_text=text(node),
                    parent_name=parent_name,
                    metadata={"language": self.language_key},
                )
            )

        def walk(node: Any, parent_container: Optional[str] = None) -> None:
            node_type = node.type

            if node_type in {"class_declaration", "class_definition"}:
                name_node = (
                    node.child_by_field_name("name") or self._first_child_of_type(node, "identifier")
                )
                class_name = text(name_node) if name_node else parent_container
                make_entity(node, name_node, EntityType.CLASS, parent_container)
                for child in node.children:
                    walk(child, class_name)
                return

            if node_type == "interface_declaration":
                name_node = node.child_by_field_name("name") or self._first_child_of_type(
                    node, "type_identifier"
                )
                make_entity(node, name_node, EntityType.INTERFACE, parent_container)
                for child in node.children:
                    walk(child, text(name_node) if name_node else parent_container)
                return

            if node_type == "enum_declaration":
                make_entity(node, node.child_by_field_name("name"), EntityType.ENUM, parent_container)
                return

            if node_type in {"function_declaration", "function_definition"}:
                make_entity(
                    node,
                    node.child_by_field_name("name") or self._first_named_identifier(node),
                    EntityType.FUNCTION,
                    parent_container,
                )
                return

            if node_type in {"method_definition", "method_declaration"}:
                name_node = (
                    node.child_by_field_name("name")
                    or self._first_named_identifier(node)
                    or self._first_child_of_type(node, "property_identifier")
                    or self._first_child_of_type(node, "field_identifier")
                )
                make_entity(node, name_node, EntityType.METHOD, parent_container)
                return

            if node_type in {"type_alias_declaration"}:
                name_node = node.child_by_field_name("name") or self._first_child_of_type(
                    node, "type_identifier"
                )
                make_entity(node, name_node, EntityType.TYPE_ALIAS, parent_container)
                return

            if node_type in {"lexical_declaration", "variable_declaration", "field_declaration"}:
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name") or self._first_named_identifier(child)
                        make_entity(child, name_node, EntityType.VARIABLE, parent_container)

            if node_type in {"var_spec", "const_spec"}:
                entity_type = EntityType.CONSTANT if node_type == "const_spec" else EntityType.VARIABLE
                for child in node.children:
                    if child.type in {"identifier", "field_identifier"}:
                        make_entity(child, child, entity_type, parent_container)

            if node_type == "type_spec":
                name_node = node.child_by_field_name("name") or self._first_child_of_type(
                    node, "type_identifier"
                )
                type_node = node.child_by_field_name("type")
                if type_node and type_node.type == "interface_type":
                    make_entity(node, name_node, EntityType.INTERFACE, parent_container)
                    return
                if type_node and type_node.type == "struct_type":
                    make_entity(node, name_node, EntityType.CLASS, parent_container)
                    return

            for child in node.children:
                walk(child, parent_container)

        walk(tree.root_node)
        return entities

    def extract_relationships(
        self, tree: Any, source_code: str, entities: List[RawEntity]
    ) -> List[RawRelationship]:
        if tree is None or getattr(tree, "root_node", None) is None:
            return []

        relationships: List[RawRelationship] = []
        source_bytes = source_code.encode("utf8")

        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")

        def scoped_name(node: Any) -> Optional[str]:
            name_node = (
                node.child_by_field_name("name")
                or self._first_named_identifier(node)
                or self._first_child_of_type(node, "property_identifier")
                or self._first_child_of_type(node, "field_identifier")
            )
            return text(name_node) if name_node else None

        def call_target(node: Any) -> Optional[str]:
            function_node = node.child_by_field_name("function")
            if not function_node:
                return None
            raw = text(function_node)
            if "." in raw:
                return raw.split(".")[-1]
            return raw

        def walk(node: Any, current_scope: Optional[str] = None) -> None:
            scope = current_scope
            node_type = node.type

            if node_type in {
                "class_declaration",
                "class_definition",
                "function_declaration",
                "function_definition",
                "method_definition",
                "method_declaration",
            }:
                scope = scoped_name(node) or scope

            if node_type in {"class_declaration", "class_definition"} and scope:
                for child in node.children:
                    if child.type in {"class_heritage", "extends_clause", "superclass"}:
                        for target in self._collect_identifier_texts(child, source_bytes):
                            relationships.append(
                                RawRelationship(
                                    source_name=scope,
                                    target_name=target,
                                    relationship_type=RelationshipType.EXTENDS,
                                )
                            )
                    if child.type in {"implements_clause", "super_interfaces"}:
                        for target in self._collect_identifier_texts(child, source_bytes):
                            relationships.append(
                                RawRelationship(
                                    source_name=scope,
                                    target_name=target,
                                    relationship_type=RelationshipType.IMPLEMENTS,
                                )
                            )

            if node_type == "type_spec" and scope:
                type_node = node.child_by_field_name("type")
                if type_node and type_node.type == "interface_type":
                    pass

            if node_type in {"call_expression", "method_invocation"} and scope:
                target = call_target(node) or scoped_name(node)
                if target:
                    relationships.append(
                        RawRelationship(
                            source_name=scope,
                            target_name=target,
                            relationship_type=RelationshipType.CALLS,
                        )
                    )

            if node_type in {"import_statement", "import_declaration", "import_spec"}:
                module_name = self._extract_import_target(node, source_bytes)
                if module_name:
                    relationships.append(
                        RawRelationship(
                            source_name="<module>",
                            target_name=module_name,
                            relationship_type=RelationshipType.IMPORTS,
                        )
                    )

            for child in node.children:
                walk(child, scope)

        walk(tree.root_node)

        for entity in entities:
            if entity.parent_name:
                relationships.append(
                    RawRelationship(
                        source_name=entity.name,
                        target_name=entity.parent_name,
                        relationship_type=RelationshipType.BELONGS_TO,
                    )
                )

        return relationships

    def _collect_identifier_texts(self, node: Any, source_bytes: bytes) -> List[str]:
        results: List[str] = []
        for child in getattr(node, "children", []):
            if child.type in {"identifier", "type_identifier", "scoped_type_identifier"}:
                results.append(source_bytes[child.start_byte:child.end_byte].decode("utf8"))
            else:
                results.extend(self._collect_identifier_texts(child, source_bytes))
        return results

    def _extract_import_target(self, node: Any, source_bytes: bytes) -> Optional[str]:
        for child in getattr(node, "children", []):
            if child.type in {"string", "interpreted_string_literal", "raw_string_literal"}:
                return source_bytes[child.start_byte:child.end_byte].decode("utf8").strip("\"'`")
            if child.type in {"identifier", "scoped_identifier"}:
                return source_bytes[child.start_byte:child.end_byte].decode("utf8")
        return None

    def _first_named_identifier(self, node: Any) -> Any:
        for child in getattr(node, "children", []):
            if child.type in {
                "identifier",
                "type_identifier",
                "property_identifier",
                "field_identifier",
            }:
                return child
        return None

    def _first_child_of_type(self, node: Any, type_name: str) -> Any:
        for child in getattr(node, "children", []):
            if child.type == type_name:
                return child
        return None
