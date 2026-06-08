"""Framework version configurations and metadata definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class FrameworkVersion:
    """Represents registered framework versions with syntactical support rules."""

    id: str
    framework_id: str
    version_string: str
    supported_syntax_rules: Dict[str, Any] = field(default_factory=dict)
