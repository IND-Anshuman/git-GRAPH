"""Symbol Resolution Engine for resolving namespaces, imports, and inheritance."""

from typing import Any, List, Optional, Dict
from src.application.semantic.resolution.global_semantic_graph import GlobalSemanticGraph, CanonicalSymbol

class SymbolResolutionEngine:
    """Extracts symbols, inheritance, aliases, imports and types from files and registers them."""

    def __init__(self, global_graph: GlobalSemanticGraph):
        self.global_graph = global_graph

    def index_file(self, file_path: str, source_code: str, tree: Any, language: str) -> None:
        """Indexes defining symbols, imports, and type bindings in a file."""
        if tree is None or getattr(tree, "root_node", None) is None:
            return

        source_bytes = source_code.encode("utf8")

        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8")

        # Convert file path to module name
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "").replace(".ts", "").replace(".js", "")

        def walk(node: Any, current_scope: Optional[str] = None) -> None:
            node_type = node.type
            scope = current_scope

            # Check class definition
            if node_type in ("class_definition", "class_declaration"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    class_name = text(name_node)
                    qname = f"{module_name}.{class_name}" if module_name else class_name
                    self.global_graph.add_symbol(CanonicalSymbol(
                        qualified_name=qname,
                        entity_type="CLASS",
                        file_path=file_path,
                        scope_id=current_scope or "global"
                    ))
                    scope = class_name
                    
                    # Inheritance extraction
                    superclasses = node.child_by_field_name("superclasses")
                    if superclasses:
                        for child in superclasses.children:
                            if child.type in ("identifier", "attribute"):
                                parent_name = text(child)
                                self.global_graph.add_alias(file_path, f"{class_name}.__parent__", parent_name)

            # Check function / method definition
            elif node_type in ("function_definition", "function_declaration", "method_definition", "method_declaration"):
                name_node = node.child_by_field_name("name")
                if name_node:
                    func_name = text(name_node)
                    if current_scope:
                        qname = f"{module_name}.{current_scope}.{func_name}"
                        entity_type = "METHOD"
                    else:
                        qname = f"{module_name}.{func_name}"
                        entity_type = "FUNCTION"
                    
                    self.global_graph.add_symbol(CanonicalSymbol(
                        qualified_name=qname,
                        entity_type=entity_type,
                        file_path=file_path,
                        scope_id=current_scope or "global"
                    ))
                    scope = f"{current_scope}.{func_name}" if current_scope else func_name

            # Check imports (Python & JS/TS)
            elif node_type in ("import_statement", "import_from_statement", "lexical_declaration", "variable_declaration"):
                if node_type == "import_from_statement":
                    # Python: from x import y as z
                    module_node = node.child_by_field_name("module_name")
                    if module_node:
                        module_name_text = text(module_node)
                        for child in node.children:
                            if child == module_node:
                                continue
                            if child.type == "dotted_name":
                                self.global_graph.add_import(file_path, module_name_text, text(child), text(child))
                            elif child.type == "aliased_import":
                                name_n = child.child_by_field_name("name")
                                alias_n = child.child_by_field_name("alias")
                                if name_n and alias_n:
                                    self.global_graph.add_import(file_path, module_name_text, text(name_n), text(alias_n))
                            elif child.type == "import_list":
                                for sub in child.children:
                                    if sub.type == "aliased_import":
                                        name_n = sub.child_by_field_name("name")
                                        alias_n = sub.child_by_field_name("alias")
                                        if name_n and alias_n:
                                            self.global_graph.add_import(file_path, module_name_text, text(name_n), text(alias_n))
                                    elif sub.type in ("dotted_name", "identifier"):
                                        self.global_graph.add_import(file_path, module_name_text, text(sub), text(sub))
                elif node_type == "import_statement":
                    # Python: import x as y; JS: import * as y from 'x' or import x from 'x'
                    # Python import statement
                    module_node = node.child_by_field_name("module_name")
                    if module_node:
                        module_name_text = text(module_node)
                        self.global_graph.add_import(file_path, module_name_text, alias=module_name_text)
                    else:
                        # Check aliased_import / dotted_name
                        for child in node.children:
                            if child.type == "dotted_name":
                                self.global_graph.add_import(file_path, text(child), alias=text(child))
                            elif child.type == "aliased_import":
                                name_n = child.child_by_field_name("name")
                                alias_n = child.child_by_field_name("alias")
                                if name_n and alias_n:
                                    self.global_graph.add_import(file_path, text(name_n), alias=text(alias_n))
                            elif child.type == "import_clause":
                                # JS/TS named/default/wildcard imports
                                source_node = node.child_by_field_name("source")
                                source_text = text(source_node).strip("'\"") if source_node else ""
                                # check children of import_clause
                                for sub in child.children:
                                    if sub.type == "named_imports":
                                        for spec in sub.children:
                                            if spec.type == "import_specifier":
                                                name_n = spec.child_by_field_name("name")
                                                alias_n = spec.child_by_field_name("alias")
                                                if name_n and alias_n:
                                                    self.global_graph.add_import(file_path, source_text, text(name_n), text(alias_n))
                                                elif name_n:
                                                    self.global_graph.add_import(file_path, source_text, text(name_n), text(name_n))
                                    elif sub.type == "namespace_import":
                                        alias_n = sub.child_by_field_name("alias") or sub.child_by_field_name("name")
                                        if alias_n:
                                            self.global_graph.add_import(file_path, source_text, alias=text(alias_n))
                                    elif sub.type == "identifier":
                                        self.global_graph.add_import(file_path, source_text, alias=text(sub))

            # Assignments/Type bindings
            elif node_type in ("assignment", "variable_declarator"):
                left = node.child_by_field_name("left") or node.child_by_field_name("name")
                right = node.child_by_field_name("right") or node.child_by_field_name("value")
                if left and right:
                    left_text = text(left)
                    right_text = text(right)
                    var_name = left_text.split(".")[-1]
                    # Check if right is a call (type instantiation)
                    # e.g., UserService() or new UserService()
                    right_clean = right_text
                    if right_clean.startswith("new "):
                        right_clean = right_clean[4:]
                    
                    if "(" in right_clean:
                        inferred_type = right_clean.split("(")[0].strip()
                        self.global_graph.bind_type(file_path, var_name, inferred_type)
                    else:
                        # Simple alias propagation
                        self.global_graph.add_alias(file_path, var_name, right_clean)

            for child in node.children:
                walk(child, scope)

        walk(tree.root_node)
