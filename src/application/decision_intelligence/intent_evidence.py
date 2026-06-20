from dataclasses import dataclass, field

@dataclass(frozen=True)
class IntentEvidence:
    supporting_commits: list[str] = field(default_factory=list)
    supporting_documents: list[str] = field(default_factory=list)
    supporting_capabilities: list[str] = field(default_factory=list)
    supporting_decisions: list[str] = field(default_factory=list)
