from src.infrastructure.extraction.compiler.compiler_context import CompilerContext
from src.domain.value_objects.intelligence_hints import ArchitectureHint
from src.infrastructure.extraction.compiler.passes.base import ICompilerPass

class Pass8ArchitectureHinting(ICompilerPass):
    """Pass 8: Architecture Hinting. Maps structural and role compositions to ArchitectureHints."""

    def execute(self, context: CompilerContext) -> None:
        # 1. Detect CQRS
        cqrs_evidence = []
        for entity in context.raw_entities:
            name_lower = entity.name.lower()
            if "commandhandler" in name_lower or "queryhandler" in name_lower:
                cqrs_evidence.append(f"Handler found: '{entity.name}'")
            elif "command" in name_lower or "query" in name_lower:
                cqrs_evidence.append(f"Message found: '{entity.name}'")
            elif "mediator" in name_lower or "mediatr" in name_lower:
                cqrs_evidence.append(f"Mediator found: '{entity.name}'")
        if len(cqrs_evidence) >= 2:
            context.architecture_hints.append(
                ArchitectureHint(
                    pattern="CQRS",
                    confidence=0.85,
                    evidence=cqrs_evidence
                )
            )

        # 2. Detect Layered Architecture
        roles = {role.role_name for role in context.inferred_roles.values()}
        layered_evidence = []
        if "Controller" in roles:
            layered_evidence.append("Controller role detected")
        if "Service" in roles:
            layered_evidence.append("Service role detected")
        if "Repository" in roles:
            layered_evidence.append("Repository role detected")
        if len(layered_evidence) >= 2:
            context.architecture_hints.append(
                ArchitectureHint(
                    pattern="Layered Architecture",
                    confidence=0.75,
                    evidence=layered_evidence
                )
            )
            
        # 3. Detect Saga
        saga_evidence = []
        for entity in context.raw_entities:
            name_lower = entity.name.lower()
            if "saga" in name_lower:
                saga_evidence.append(f"Saga component found: '{entity.name}'")
        if saga_evidence:
            context.architecture_hints.append(
                ArchitectureHint(
                    pattern="Saga",
                    confidence=0.9,
                    evidence=saga_evidence
                )
            )
            
        # 4. Detect Hexagonal (Ports & Adapters)
        hex_evidence = []
        for entity in context.raw_entities:
            name_lower = entity.name.lower()
            if "port" in name_lower:
                hex_evidence.append(f"Port found: '{entity.name}'")
            elif "adapter" in name_lower:
                hex_evidence.append(f"Adapter found: '{entity.name}'")
        if len(hex_evidence) >= 2:
            context.architecture_hints.append(
                ArchitectureHint(
                    pattern="Hexagonal Architecture",
                    confidence=0.8,
                    evidence=hex_evidence
                )
            )
