from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.domain.enums.analysis_status import AnalysisStatus
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class RepositoryEntity:
    """Entity representing a tracked source code repository."""
    id: RepositoryId
    name: str
    url: str
    default_branch: str
    local_path: str | None
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def mark_cloning(self) -> None:
        self.status = AnalysisStatus.CLONING
        self.updated_at = datetime.now(timezone.utc)

    def mark_scanning(self) -> None:
        self.status = AnalysisStatus.SCANNING
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        self.status = AnalysisStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, reason: str) -> None:
        self.status = AnalysisStatus.FAILED
        self.metadata["failure_reason"] = reason
        self.updated_at = datetime.now(timezone.utc)
