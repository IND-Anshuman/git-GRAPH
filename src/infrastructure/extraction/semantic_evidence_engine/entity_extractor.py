from typing import Any, Optional
from src.domain.enums.entity_type import EntityType
from src.infrastructure.extraction.strategies.base import RawEntity
from src.infrastructure.extraction.semantic_evidence_engine.source_span import SourceSpan
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

class EntityExtractor(IBaseExtractor):
    """Pass 1 Entity Extractor. Walks the tree-sitter AST and extracts basic syntactic entities."""
    
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
            
        def walk(node: Any, parent_container: Optional[str] = None, decorators: Optional[list] = None) -> None:
            node_type = node.type
            current_decorators = decorators or []
            
            # Support Python decorated definition
            if node_type == "decorated_definition":
                decs = []
                defn = None
                for child in node.children:
                    if child.type == "decorator":
                        decs.append(text(child).strip())
                    elif child.type in {"class_declaration", "class_definition", "function_declaration", "function_definition", "method_definition", "method_declaration"}:
                        defn = child
                if defn:
                    walk(defn, parent_container, decs)
                return
                
            # Class
            if node_type in {"class_declaration", "class_definition"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    class_name = text(name_node)
                    entity = RawEntity(
                        name=class_name,
                        entity_type=EntityType.CLASS,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    for child in node.children:
                        walk(child, class_name)
                    return
            
            # Interface
            elif node_type == "interface_declaration":
                name_node = node.child_by_field_name("name")
                if name_node:
                    iface_name = text(name_node)
                    entity = RawEntity(
                        name=iface_name,
                        entity_type=EntityType.INTERFACE,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    for child in node.children:
                        walk(child, iface_name)
                    return
            
            # Enum
            elif node_type == "enum_declaration":
                name_node = node.child_by_field_name("name")
                if name_node:
                    enum_name = text(name_node)
                    entity = RawEntity(
                        name=enum_name,
                        entity_type=EntityType.ENUM,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    return
            
            # Function
            elif node_type in {"function_declaration", "function_definition"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    func_name = text(name_node)
                    entity = RawEntity(
                        name=func_name,
                        entity_type=EntityType.FUNCTION,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    return
            
            # Method
            elif node_type in {"method_definition", "method_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    method_name = text(name_node)
                    entity = RawEntity(
                        name=method_name,
                        entity_type=EntityType.METHOD,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    return
 
            # Variable Declarators
            elif node_type == "variable_declarator":
                name_node = node.child_by_field_name("name")
                if name_node:
                    var_name = text(name_node)
                    val_node = node.child_by_field_name("value")
                    is_func = False
                    if val_node and val_node.type in {"arrow_function", "function", "generator_function"}:
                        is_func = True
                    entity = RawEntity(
                        name=var_name,
                        entity_type=EntityType.FUNCTION if is_func else EntityType.VARIABLE,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_column=node.start_point[1] + 1,
                        end_column=node.end_point[1] + 1,
                        source_text=text(node),
                        parent_name=parent_container,
                        span=make_span(node),
                        metadata={"decorators": current_decorators}
                    )
                    ir.entities.append(entity)
                    
            for child in node.children:
                walk(child, parent_container)
                
        walk(tree.root_node)
