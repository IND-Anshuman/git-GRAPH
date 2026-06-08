"""Intermediate Semantic Representation: CanonicalContext definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class FrameworkInfo:
    """Captured framework name and version string."""

    name: str
    version: str


@dataclass
class CanonicalContext:
    """Surrounding environmental configuration context variables."""

    repository_id: str
    commit_hash: str
    frameworks: List[FrameworkInfo] = field(default_factory=list)
    environment: str = "Production"
    global_configurations: Dict[str, Any] = field(default_factory=dict)
