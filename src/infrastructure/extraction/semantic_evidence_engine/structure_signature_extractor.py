from typing import Any, Optional
from src.infrastructure.extraction.semantic_evidence_engine.extractor_registry import IBaseExtractor
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR
from src.infrastructure.extraction.semantic_evidence_engine.raw_structure_signature import RawStructureSignature
from src.domain.value_objects.knowledge_confidence import KnowledgeConfidence

class StructureSignatureExtractor(IBaseExtractor):
    """Pass 1 Structure Signature Extractor. Computes structural metric counts on entities."""

    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        if tree is None or getattr(tree, "root_node", None) is None:
            return
            
        def find_node(node: Any, start_byte: int, end_byte: int) -> Optional[Any]:
            if node.start_byte == start_byte and node.end_byte == end_byte:
                return node
            for child in node.children:
                res = find_node(child, start_byte, end_byte)
                if res:
                    return res
            return None

        for entity in ir.entities:
            if entity.span is None:
                continue
                
            class_node = find_node(tree.root_node, entity.span.start_byte, entity.span.end_byte)
            if not class_node:
                continue
                
            # Count child metrics
            method_count = 0
            property_count = 0
            dependency_count = 0
            nested_count = 0
            statement_count = 0
            cyclomatic_indicators = 0
            
            def count_metrics(node: Any):
                nonlocal method_count, property_count, dependency_count, nested_count, statement_count, cyclomatic_indicators
                
                for child in node.children:
                    nt = child.type
                    if nt in {"function_definition", "method_definition"}:
                        method_count += 1
                    elif nt in {"variable_declarator", "assignment", "field_declaration"}:
                        property_count += 1
                    elif nt in {"import_statement", "import_declaration"}:
                        dependency_count += 1
                    elif nt in {"class_declaration", "class_definition"}:
                        nested_count += 1
                    elif nt in {"expression_statement", "lexical_declaration"}:
                        statement_count += 1
                    elif nt in {"if_statement", "for_statement", "while_statement", "try_statement", "except_clause", "case_statement"}:
                        cyclomatic_indicators += 1
                        
                    # Recurse unless it's a nested class to avoid mixing scopes
                    if nt not in {"class_declaration", "class_definition"}:
                        count_metrics(child)
                        
            count_metrics(class_node)
            
            # Count extends/implements from relationships
            inheritance_depth = 0
            for rel in ir.relationships:
                if rel.source_name == entity.name and getattr(rel.relationship_type, "name", None) in ("EXTENDS", "IMPLEMENTS"):
                    inheritance_depth += 1
            
            sig = RawStructureSignature(
                entity_id=entity.name,
                kind=entity.entity_type.name if hasattr(entity.entity_type, "name") else str(entity.entity_type),
                method_count=method_count,
                property_count=property_count,
                dependency_count=dependency_count,
                inheritance_depth=inheritance_depth,
                nested_entity_count=nested_count,
                statement_count=statement_count,
                cyclomatic_indicators=cyclomatic_indicators,
                confidence=KnowledgeConfidence(1.0, "AST_MATCH", ["structure_metrics"])
            )
            ir.structure_signatures.append(sig)
            entity.structure_signature = sig
