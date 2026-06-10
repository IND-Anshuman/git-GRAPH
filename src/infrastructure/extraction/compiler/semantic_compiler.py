from typing import Dict, Any
from src.domain.entities.semantic_compiler_context import SemanticCompilerContext
from src.infrastructure.extraction.compiler.passes.pass1_ast_extraction import Pass1ASTExtraction
from src.infrastructure.extraction.compiler.passes.pass2_framework_resolution import Pass2FrameworkResolution
from src.infrastructure.extraction.compiler.passes.pass3_semantic_role_inference import Pass3SemanticRoleInference
from src.infrastructure.extraction.compiler.passes.pass4_hint_extraction import Pass4HintExtraction
from src.infrastructure.extraction.compiler.passes.pass5_relationship_inference import Pass5RelationshipInference
from src.infrastructure.extraction.compiler.passes.pass6_flow_compilation import Pass6FlowCompilation
from src.infrastructure.extraction.compiler.passes.pass7_capability_hinting import Pass7CapabilityHinting
from src.infrastructure.extraction.compiler.passes.pass8_architecture_hinting import Pass8ArchitectureHinting
from src.infrastructure.extraction.compiler.passes.pass9_isr_generation import Pass9ISRGeneration

class SemanticCompiler:
    """The master Semantic Compiler V1 orchestrating all 9 compilation passes."""
    
    def __init__(self):
        self.passes = [
            Pass1ASTExtraction(),
            Pass2FrameworkResolution(),
            Pass3SemanticRoleInference(),
            Pass4HintExtraction(),
            Pass5RelationshipInference(),
            Pass6FlowCompilation(),
            Pass7CapabilityHinting(),
            Pass8ArchitectureHinting(),
            Pass9ISRGeneration()
        ]

    def compile(self, file_path: str, source_code: str, language: str, project_metadata: Dict[str, Any] | None = None) -> SemanticCompilerContext:
        """Executes the 9-Pass Compiler pipeline using an isolated, shared SemanticCompilerContext."""
        context = SemanticCompilerContext(
            language=language,
            source_code=source_code,
            file_path=file_path,
            project_metadata=project_metadata or {}
        )
        
        for comp_pass in self.passes:
            comp_pass.execute(context)
            
        return context
