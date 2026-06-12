from abc import ABC, abstractmethod
from src.infrastructure.extraction.compiler.compiler_context import CompilerContext

class ICompilerPass(ABC):
    @abstractmethod
    def execute(self, context: CompilerContext) -> None:
        """Execute the compiler pass, mutating the context."""
        pass
