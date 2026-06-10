from abc import ABC, abstractmethod
from src.domain.entities.semantic_compiler_context import SemanticCompilerContext

class ICompilerPass(ABC):
    @abstractmethod
    def execute(self, context: SemanticCompilerContext) -> None:
        """Execute the compiler pass, mutating the context."""
        pass
