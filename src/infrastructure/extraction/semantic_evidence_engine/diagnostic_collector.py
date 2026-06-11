"""Compiler diagnostic collector extractor."""

from typing import Any
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.compiler_diagnostic import CompilerDiagnostic

class DiagnosticCollector(IBaseExtractor):
    """Pass 1 Diagnostic Collector. Walks the tree-sitter AST and collects compiler diagnostics."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None:
            ir.diagnostics.append(
                CompilerDiagnostic(
                    severity="ERROR",
                    category="PARSING",
                    code="NULL_AST",
                    message=f"Parser returned null AST for file: {file_path}",
                    evidence=[file_path]
                )
            )
            return

        if getattr(tree, "root_node", None) is None:
            ir.diagnostics.append(
                CompilerDiagnostic(
                    severity="ERROR",
                    category="PARSING",
                    code="EMPTY_ROOT",
                    message=f"AST has no root node for file: {file_path}",
                    evidence=[file_path]
                )
            )
            return

        source_bytes = source_code.encode("utf8")

        def text(node: Any) -> str:
            return source_bytes[node.start_byte:node.end_byte].decode("utf8", errors="replace")

        def walk(node: Any) -> None:
            if node.type == "ERROR":
                node_text = text(node)
                start_line = node.start_point[0] + 1
                start_col = node.start_point[1] + 1
                message = f"Syntax error in {file_path} at line {start_line}, col {start_col}"
                if node_text:
                    message += f": '{node_text}'"
                
                ir.diagnostics.append(
                    CompilerDiagnostic(
                        severity="ERROR",
                        category="PARSING",
                        code="SYNTAX_ERROR",
                        message=message,
                        evidence=[node_text]
                    )
                )
            
            # Recurse through children
            for child in node.children:
                walk(child)

        walk(tree.root_node)
