from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Provenance:
    """Tracks the creator and timestamp for an piece of extracted evidence."""
    extractor: str
    extraction_version: str
    extraction_timestamp: datetime
