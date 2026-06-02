from dataclasses import dataclass, field
from datetime import datetime
from src.domain.value_objects.repository_id import RepositoryId

@dataclass
class Commit:
    """Entity representing a Git commit event in the repository's history."""
    hash: str
    repository_id: RepositoryId
    author: str
    email: str
    timestamp: datetime
    message: str
    parent_hashes: list[str] = field(default_factory=list)

    @property
    def is_merge(self) -> bool:
        """Returns True if the commit is a merge commit (has multiple parents)."""
        return len(self.parent_hashes) > 1

    @property
    def is_root(self) -> bool:
        """Returns True if the commit is a root commit (has no parents)."""
        return len(self.parent_hashes) == 0
