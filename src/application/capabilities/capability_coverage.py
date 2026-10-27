"""Domain model representing capability coverage mapping."""

from dataclasses import dataclass, field


@dataclass
class CapabilityCoverage:
    """Detailed mapping of specific source code and resource elements covered by a capability."""

    entities: list[str] = field(default_factory=list)  # List of entity SEIDs
    flows: list[str] = field(default_factory=list)  # List of flow paths
    apis: list[str] = field(default_factory=list)  # List of endpoint paths/FQNs
    databases: list[str] = field(default_factory=list)  # List of database tables/models
    queues: list[str] = field(default_factory=list)  # List of message topics/queues
    agents: list[str] = field(default_factory=list)  # List of AI Agent names/roles
    models: list[str] = field(default_factory=list)  # List of LLMs invoked
