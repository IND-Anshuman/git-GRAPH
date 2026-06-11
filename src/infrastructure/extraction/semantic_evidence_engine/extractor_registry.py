from typing import List, Type, Any
from abc import ABC, abstractmethod
from src.infrastructure.extraction.semantic_evidence_engine.evidence_ir import EvidenceIR

class IBaseExtractor(ABC):
    """Base interface for all SEEE sub-extractors."""
    
    @abstractmethod
    def extract(self, tree: Any, source_code: str, file_path: str, ir: EvidenceIR) -> None:
        """Analyze the tree-sitter AST and populate/mutate the mutable EvidenceIR."""
        pass

class ExtractorRegistry:
    """Registry to register and resolve all pipeline extractors dynamically."""
    
    def __init__(self) -> None:
        self._extractors: List[Type[IBaseExtractor]] = []

    def register(self, extractor_class: Type[IBaseExtractor]) -> None:
        if extractor_class not in self._extractors:
            self._extractors.append(extractor_class)

    def get_extractors(self) -> List[IBaseExtractor]:
        return [cls() for cls in self._extractors]
