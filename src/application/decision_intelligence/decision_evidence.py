from dataclasses import dataclass, field

@dataclass(frozen=True)
class DecisionEvidence:
    supporting_commits: list[str] = field(default_factory=list)
    supporting_documents: list[str] = field(default_factory=list)
    supporting_capabilities: list[str] = field(default_factory=list)
    supporting_architecture_changes: list[str] = field(default_factory=list)
    supporting_repository_events: list[str] = field(default_factory=list)
