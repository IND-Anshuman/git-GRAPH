from typing import Any, Optional, List
from src.domain.enums.relationship_type import RelationshipType
from src.infrastructure.extraction.strategies.base import RawRelationship
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

class RelationshipExtractor(IBaseExtractor):
    """Pass 1 Relationship Extractor. Extracts pure syntactic relationships (extends, implements, calls, imports)."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return
            
        source_bytes = source_code.encode("utf8")
        
        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")
            
        def make_span(node: Any) -> SourceSpan:
            return SourceSpan(
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                start_column=node.start_point[1] + 1,
                end_line=node.end_point[0] + 1,
                end_column=node.end_point[1] + 1,
                start_byte=node.start_byte,
                end_byte=node.end_byte
            )

        def walk(node: Any, current_scope: Optional[str] = None) -> None:
            scope = current_scope
            node_type = node.type
            
            if node_type in {
                "class_declaration",
                "class_definition",
                "function_declaration",
                "function_definition",
                "method_definition",
                "method_declaration"
            }:
                name_node = node.child_by_field_name("name")
                if name_node:
                    scope = text(name_node)
            
            # EXTENDS / IMPLEMENTS
            if node_type in {"class_declaration", "class_definition"} and scope:
                for child in node.children:
                    # JS/TS: class_heritage / extends_clause / superclass
                    if child.type in {"class_heritage", "extends_clause", "superclass"}:
                        for target in self._collect_identifiers(child, source_bytes):
                            rel = RawRelationship(
                                source_name=scope,
                                target_name=target,
                                relationship_type=RelationshipType.EXTENDS,
                                span=make_span(child)
                            )
                            ir.relationships.append(rel)
                    # Python: class X(A, B, C) — base classes live in argument_list
                    elif child.type == "argument_list":
                        for target in self._collect_identifiers(child, source_bytes):
                            rel = RawRelationship(
                                source_name=scope,
                                target_name=target,
                                relationship_type=RelationshipType.EXTENDS,
                                span=make_span(child)
                            )
                            ir.relationships.append(rel)
                    if child.type in {"implements_clause", "super_interfaces"}:
                        for target in self._collect_identifiers(child, source_bytes):
                            rel = RawRelationship(
                                source_name=scope,
                                target_name=target,
                                relationship_type=RelationshipType.IMPLEMENTS,
                                span=make_span(child)
                            )
                            ir.relationships.append(rel)

            # CALLS
            elif node_type in {"call", "call_expression", "method_invocation"} and scope:
                func_node = node.child_by_field_name("function")
                if func_node:
                    target = text(func_node)
                    if "." in target:
                        target = target.split(".")[-1]
                    rel = RawRelationship(
                        source_name=scope,
                        target_name=target,
                        relationship_type=RelationshipType.CALLS,
                        span=make_span(node)
                    )
                    ir.relationships.append(rel)

            # IMPORTS
            elif node_type in {"import_statement", "import_declaration", "import_from_statement"}:
                target = None
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    target = text(module_node)
                else:
                    for child in getattr(node, "children", []):
                        if child.type == "aliased_import":
                            # Python: 'import redis as r' → extract dotted_name child
                            for sub in child.children:
                                if sub.type == "dotted_name":
                                    target = text(sub)
                                    break
                            if target is None:
                                target = text(child)  # fallback
                            break
                        if child.type in {"dotted_name"}:
                            target = text(child)
                            break
                        if child.type in {"string", "string_literal", "interpreted_string_literal", "raw_string_literal"}:
                            target = text(child).strip("\"'`")
                            break
                        if child.type in {"identifier", "scoped_identifier"}:
                            target = text(child)
                            break
                if target:
                    rel = RawRelationship(
                        source_name="<module>",
                        target_name=target,
                        relationship_type=RelationshipType.IMPORTS,
                        span=make_span(node)
                    )
                    ir.relationships.append(rel)

            for child in node.children:
                walk(child, scope)

        walk(tree.root_node)
        
        # Add CONTAINS relationships dynamically
        for entity in ir.entities:
            if entity.parent_name:
                rel = RawRelationship(
                    source_name=entity.parent_name,
                    target_name=entity.name,
                    relationship_type=RelationshipType.CONTAINS,
                    span=entity.span
                )
                ir.relationships.append(rel)

    def _collect_identifiers(self, node: Any, source_bytes: bytes) -> List[str]:
        results = []
        for child in getattr(node, "children", []):
            if child.type in {"identifier", "type_identifier", "scoped_type_identifier"}:
                results.append(source_bytes[child.start_byte:child.end_byte].decode("utf8"))
            else:
                results.extend(self._collect_identifiers(child, source_bytes))
        return results

    def _find_first_string_child(self, node: Any) -> Optional[Any]:
        for child in getattr(node, "children", []):
            if child.type in {"string", "string_literal"}:
                return child
        return None
