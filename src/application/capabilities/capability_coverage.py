"""Domain model representing capability coverage mapping."""

from dataclasses import dataclass, field
from typing import List

@dataclass
class CapabilityCoverage:
    """Detailed mapping of specific source code and resource elements covered by a capability."""
    entities: List[str] = field(default_factory=list)  # List of entity SEIDs
    flows: List[str] = field(default_factory=list)     # List of flow paths
    apis: List[str] = field(default_factory=list)      # List of endpoint paths/FQNs
    databases: List[str] = field(default_factory=list) # List of database tables/models
    queues: List[str] = field(default_factory=list)    # List of message topics/queues
    agents: List[str] = field(default_factory=list)    # List of AI Agent names/roles
    models: List[str] = field(default_factory=list)    # List of LLMs invoked
