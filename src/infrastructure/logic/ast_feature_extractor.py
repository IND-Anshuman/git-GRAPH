"""Tree-sitter implementation of IASTFeatureExtractor."""

import re
from typing import Any, List, Optional

from src.application.ports.ast_feature_port import (
    ASTFeatures,
    ExtractedFeature,
    IASTFeatureExtractor,
)


class TreeSitterASTFeatureExtractor(IASTFeatureExtractor):
    """Extracts behavioral and structural features from a Tree-sitter AST."""

    def extract_features(
        self, tree: Any, source_code: str, start_line: int, end_line: int
    ) -> ASTFeatures:
        """
        Walk the AST to extract features in the line range [start_line, end_line].

        Note: Line range is 1-indexed. Tree-sitter is 0-indexed.
        """
        source_bytes = source_code.encode("utf-8")
        features = ASTFeatures()

        # Phase 1: Extract module-level imports (since function calls depend on them)
        self._extract_module_imports(tree.root_node, source_bytes, features)

        # Phase 2: Identify parameters of the target function to track data flow
        params = self._find_function_parameters(
            tree.root_node, start_line, end_line, source_bytes
        )

        # Phase 3: Walk the AST within the target line range
        self._walk_and_extract(
            tree.root_node, start_line, end_line, source_bytes, params, features
        )

        return features

    def _extract_module_imports(
        self, node: Any, source_bytes: bytes, features: ASTFeatures
    ) -> None:
        """Scan the entire file for imports."""
        if node.type in ("import_statement", "import_from_statement"):
            line = node.start_point[0] + 1
            text = source_bytes[node.start_byte : node.end_byte].decode("utf-8")

            if node.type == "import_statement":
                # import bcrypt, hashlib
                # children might contain dotted_name
                for child in node.children:
                    if child.type == "dotted_name":
                        symbol = source_bytes[
                            child.start_byte : child.end_byte
                        ].decode("utf-8")
                        features.imports.append(
                            ExtractedFeature(
                                feature_type="import",
                                symbol=f"import:{symbol}",
                                line_number=line,
                                metadata={"raw": text},
                            )
                        )
            elif node.type == "import_from_statement":
                # from datetime import datetime
                # module_name node is the source
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    module_name = source_bytes[
                        module_node.start_byte : module_node.end_byte
                    ].decode("utf-8")
                    features.imports.append(
                        ExtractedFeature(
                            feature_type="import",
                            symbol=f"import:{module_name}",
                            line_number=line,
                            metadata={"raw": text},
                        )
                    )
                    # Also collect individual imported names
                    # e.g., from passlib.context import CryptContext
                    # we want to record the individual imported symbols
                    for child in node.children:
                        if child.type == "dotted_name":
                            sym = source_bytes[
                                child.start_byte : child.end_byte
                            ].decode("utf-8")
                            features.imports.append(
                                ExtractedFeature(
                                    feature_type="import",
                                    symbol=f"import:{module_name}.{sym}",
                                    line_number=line,
                                    metadata={"raw": text},
                                )
                            )

        for child in node.children:
            self._extract_module_imports(child, source_bytes, features)

    def _find_function_parameters(
        self, node: Any, start_line: int, end_line: int, source_bytes: bytes
    ) -> List[str]:
        """Find parameters of the function definition enclosing or matching the range."""
        if node.type == "function_definition":
            func_start = node.start_point[0] + 1
            func_end = node.end_point[0] + 1
            # If this function matches our line range
            if func_start <= start_line and func_end >= end_line:
                params_node = node.child_by_field_name("parameters")
                if params_node:
                    params = []
                    for child in params_node.children:
                        if child.type in (
                            "identifier",
                            "typed_parameter",
                            "default_parameter",
                        ):
                            ident = child
                            if child.type == "typed_parameter":
                                ident = child.child(0)
                            elif child.type == "default_parameter":
                                ident = child.child_by_field_name("name")

                            if ident and ident.type == "identifier":
                                p_name = source_bytes[
                                    ident.start_byte : ident.end_byte
                                ].decode("utf-8")
                                params.append(p_name)
                    return params

        for child in node.children:
            res = self._find_function_parameters(
                child, start_line, end_line, source_bytes
            )
            if res:
                return res
        return []

    def _walk_and_extract(
        self,
        node: Any,
        start_line: int,
        end_line: int,
        source_bytes: bytes,
        params: List[str],
        features: ASTFeatures,
    ) -> None:
        """Walk the AST to extract features from nodes in the line range."""
        node_start = node.start_point[0] + 1
        node_end = node.end_point[0] + 1

        # Skip nodes completely outside the target line range
        if node_end < start_line or node_start > end_line:
            return

        if node.type == "call":
            self._extract_call(node, source_bytes, params, features)

        elif node.type == "decorator":
            self._extract_decorator(node, source_bytes, features)

        elif node.type in ("comparison_operator", "comparison"):
            self._extract_comparison(node, source_bytes, features)

        elif node.type == "string":
            self._extract_string(node, source_bytes, features)

        elif node.type == "subscript":
            self._extract_subscript(node, source_bytes, features)

        for child in node.children:
            self._walk_and_extract(
                child, start_line, end_line, source_bytes, params, features
            )

    def _extract_call(
        self, node: Any, source_bytes: bytes, params: List[str], features: ASTFeatures
    ) -> None:
        """Extract a function call and trace simple data flow from parameters."""
        line = node.start_point[0] + 1
        func_node = node.child_by_field_name("function")
        if not func_node:
            return

        func_name = source_bytes[
            func_node.start_byte : func_node.end_byte
        ].decode("utf-8")

        # Record call feature
        features.calls.append(
            ExtractedFeature(
                feature_type="call",
                symbol=f"call:{func_name}",
                line_number=line,
                metadata={"raw": func_name},
            )
        )

        # Simplify method call lookup: e.g., if it's bcrypt.checkpw, register checkpw as well
        if "." in func_name:
            method_name = func_name.split(".")[-1]
            features.calls.append(
                ExtractedFeature(
                    feature_type="call",
                    symbol=f"call:{method_name}",
                    line_number=line,
                    metadata={"raw": func_name, "parent": func_name},
                )
            )

        # Extract arguments for simple data flow tracing
        arg_list_node = node.child_by_field_name("arguments")
        if arg_list_node:
            for arg in arg_list_node.children:
                if arg.type == "identifier":
                    arg_name = source_bytes[
                        arg.start_byte : arg.end_byte
                    ].decode("utf-8")
                    if arg_name in params:
                        # Param flows to call: register data flow
                        features.data_flows.append(
                            {
                                "source": arg_name,
                                "sink": func_name,
                                "path": [arg_name, func_name],
                                "line": line,
                            }
                        )

    def _extract_decorator(
        self, node: Any, source_bytes: bytes, features: ASTFeatures
    ) -> None:
        """Extract a decorator definition."""
        line = node.start_point[0] + 1
        # The child is usually an identifier or a call
        name_node = node.child(1)  # Skip the '@' character
        if name_node:
            dec_name = source_bytes[
                name_node.start_byte : name_node.end_byte
            ].decode("utf-8")
            if "(" in dec_name:
                dec_name = dec_name.split("(")[0]

            features.decorators.append(
                ExtractedFeature(
                    feature_type="decorator",
                    symbol=f"decorator:{dec_name}",
                    line_number=line,
                    metadata={"raw": dec_name},
                )
            )

    def _extract_comparison(
        self, node: Any, source_bytes: bytes, features: ASTFeatures
    ) -> None:
        """Extract comparison operators."""
        line = node.start_point[0] + 1
        # In tree-sitter comparisons, the operator is a child node
        # e.g., '==', '!=', 'in', etc.
        for child in node.children:
            if child.type in ("==", "!=", "in", "not in", "<", ">", "<=", ">="):
                op = child.type
                features.comparisons.append(
                    ExtractedFeature(
                        feature_type="comparison",
                        symbol=f"operator:{op}",
                        line_number=line,
                        metadata={"operator": op},
                    )
                )

    def _extract_string(
        self, node: Any, source_bytes: bytes, features: ASTFeatures
    ) -> None:
        """Extract strings and check if they look like SQL statements or sensitive keys."""
        line = node.start_point[0] + 1
        text = source_bytes[node.start_byte : node.end_byte].decode("utf-8")
        # Strip outer quotes
        clean_text = text.strip("'\" \r\n\t")

        # Check for SQL keywords
        sql_keywords = r"^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b"
        if re.search(sql_keywords, clean_text, re.IGNORECASE):
            features.strings.append(
                ExtractedFeature(
                    feature_type="string",
                    symbol="string:sql_keyword",
                    line_number=line,
                    metadata={"raw": clean_text},
                )
            )

    def _extract_subscript(
        self, node: Any, source_bytes: bytes, features: ASTFeatures
    ) -> None:
        """Extract subscripts (e.g. cache dictionary lookups)."""
        line = node.start_point[0] + 1
        text = source_bytes[node.start_byte : node.end_byte].decode("utf-8")
        features.subscripts.append(
            ExtractedFeature(
                feature_type="subscript",
                symbol="struct:comparison"
                if "compare" in text
                else "struct:subscript",
                line_number=line,
                metadata={"raw": text},
            )
        )
