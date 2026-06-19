"""Cache for expensive architectural calculations."""

from typing import Any, Dict, Optional, Tuple

class ArchitectureCache:
    """
    In-memory or distributed cache for architecture calculations like cycles,
    fitness scores, and bounded contexts.
    Keys are typically (repository_id, commit_hash, analysis_type).
    """

    def __init__(self) -> None:
        """Initialize the architecture cache."""
        self._cache: Dict[Tuple[str, str, str], Any] = {}

    def get(self, repository_id: str, commit_hash: str, analysis_type: str) -> Optional[Any]:
        """Retrieve a cached value."""
        key = (repository_id, commit_hash, analysis_type)
        return self._cache.get(key)

    def set(self, repository_id: str, commit_hash: str, analysis_type: str, value: Any) -> None:
        """Store a value in the cache."""
        key = (repository_id, commit_hash, analysis_type)
        self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def invalidate(self, repository_id: str, commit_hash: str) -> None:
        """Invalidate all cache entries for a specific repository and commit."""
        keys_to_remove = [k for k in self._cache.keys() if k[0] == repository_id and k[1] == commit_hash]
        for k in keys_to_remove:
            del self._cache[k]
