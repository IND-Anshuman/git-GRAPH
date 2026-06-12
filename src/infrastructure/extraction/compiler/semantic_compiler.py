from typing import Dict, Any
from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.application.dtos.compiler_output import CompilerOutput
from src.domain.enums.language import SupportedLanguage
from src.infrastructure.parsing.language_registry import LanguageRegistry
from src.infrastructure.extraction.semantic_evidence_engine.semantic_evidence_engine import SemanticEvidenceExtractionEngine

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

    def compile(self, file_path: str, source_code: str, language: str, project_metadata: Dict[str, Any] | None = None) -> CompilerOutput:
        """Executes the 9-Pass Compiler pipeline using an isolated, shared CompilerContext."""
        # 1. Resolve language and parse tree-sitter AST
        lang_str = language.upper() if isinstance(language, str) else language.name
        try:
            lang_enum = SupportedLanguage[lang_str]
        except KeyError:
            if isinstance(language, SupportedLanguage):
                lang_enum = language
            else:
                lang_enum = SupportedLanguage.UNKNOWN
        
        language_registry = LanguageRegistry()
        adapter = language_registry.get_adapter(lang_enum)
        
        extraction_result = None
        if adapter:
            parser = adapter.get_parser()
            tree = parser.parse(bytes(source_code, "utf8"))
            # 2. Call SEEE directly once at the start
            engine = SemanticEvidenceExtractionEngine()
            extraction_result = engine.extract(tree, source_code, file_path)
            
        # 3. Instantiate the infrastructure-scoped CompilerContext
        context = CompilerContext(
            language=language,
            source_code=source_code,
            file_path=file_path,
            project_metadata=project_metadata or {},
            extraction_result=extraction_result
        )
        
        # 4. Run all 9 passes
        for comp_pass in self.passes:
            comp_pass.execute(context)
            
        # 5. Assemble and return CompilerOutput DTO
        return CompilerOutput(
            generated_entities=context.generated_entities,
            generated_relationships=context.generated_relationships,
            report=context.report,
            frameworks_detected=context.frameworks_detected,
            semantic_hints=context.semantic_hints
        )
