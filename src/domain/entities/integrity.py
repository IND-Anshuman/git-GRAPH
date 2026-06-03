from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import List, Dict, Any

@dataclass
class IntegrityViolation:
    """Domain entity representing a structural validation issue within the temporal graph."""
    id: uuid.UUID
    repository_id: uuid.UUID
    violation_type: str
    severity: str
    target_seid: str | None
    description: str
    recommended_repair: str
    is_resolved: bool
    detected_at: datetime

@dataclass
class RepairAudit:
    """Domain entity representing a record of an executed repair transaction."""
    id: uuid.UUID
    repository_id: uuid.UUID
    operator: str
    issue_ids: List[uuid.UUID]
    repair_actions: List[Dict[str, Any]]
    executed_at: datetime
