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
        self._extractor_classes: List[Type[IBaseExtractor]] = []
        self._instances: List[IBaseExtractor] = []

    def register(self, extractor_class: Type[IBaseExtractor]) -> None:
        if extractor_class not in self._extractor_classes:
            self._extractor_classes.append(extractor_class)
            self._instances.append(extractor_class())

    def get_extractors(self) -> List[IBaseExtractor]:
        return self._instances
