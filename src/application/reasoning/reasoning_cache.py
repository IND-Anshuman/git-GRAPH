"""
Phase 7A — ReasoningCache

Thread-safe, in-memory cache for ``ReasoningResult`` objects.

Cache key
---------
    (repository_id, commit_hash, question_type, normalized_query)

Normalisation: lowercase + strip all whitespace runs to a single space.

Invalidation
------------
The cache does NOT automatically invalidate.  Callers must call
``invalidate(repository_id)`` when:
  * A new commit is ingested for the repository.
  * Capabilities are recomputed.
  * The concept graph is rebuilt.

This is intentionally conservative — correctness over performance.

Phase 8 note
------------
When the UI supports repeated identical queries, the cache will become
critical.  The current design supports a future TTL-based invalidation
without changing the public interface.
"""

from __future__ import annotations

import threading
import logging
import re
from typing import Optional

from src.application.reasoning.reasoning_question_type import ReasoningQuestionType
from src.application.reasoning.reasoning_result import ReasoningResult

logger = logging.getLogger(__name__)

CacheKey = tuple[str, str, str, str]


def _normalize_query(query: str) -> str:
    """Lowercase and collapse whitespace for cache key normalisation."""
    return re.sub(r"\s+", " ", query.strip().lower())


class ReasoningCache:
    """Thread-safe in-memory cache for deterministic reasoning results.

    All methods are safe to call concurrently from multiple threads.
    The internal lock uses a ``threading.RLock`` (re-entrant) so that the
    same thread can call ``get`` and ``put`` without deadlock.

    Usage::

        cache = ReasoningCache()
        key   = cache.make_key(repo_id, commit_hash, question_type, query)
        hit   = cache.get(key)
        if hit is None:
            result = engine.execute(...)
            cache.put(key, result)
    """

    def __init__(self, max_size: int = 512) -> None:
        self._store: dict[CacheKey, ReasoningResult] = {}
        self._lock = threading.RLock()
        self._max_size = max_size

    # ── Public API ────────────────────────────────────────────────────────────

    @staticmethod
    def make_key(
        repository_id: str,
        commit_hash: str,
        question_type: ReasoningQuestionType,
        query: str,
    ) -> CacheKey:
        """Build a canonical cache key tuple."""
        return (
            str(repository_id),
            str(commit_hash),
            question_type.value,
            _normalize_query(query),
        )

    def get(self, key: CacheKey) -> Optional[ReasoningResult]:
        """Return the cached result for *key*, or None on a cache miss."""
        with self._lock:
            result = self._store.get(key)
            if result is not None:
                logger.debug("ReasoningCache HIT: key=%r", key)
            else:
                logger.debug("ReasoningCache MISS: key=%r", key)
            return result

    def put(self, key: CacheKey, result: ReasoningResult) -> None:
        """Store *result* under *key*.

        If the cache exceeds ``max_size``, the oldest 10% of entries are
        evicted (simple FIFO — adequate for Phase 7A).
        """
        with self._lock:
            if len(self._store) >= self._max_size:
                self._evict()
            self._store[key] = result
            logger.debug(
                "ReasoningCache PUT: key=%r (cache_size=%d)", key, len(self._store)
            )

    def invalidate(self, repository_id: str) -> int:
        """Remove all cached results for *repository_id*.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            keys_to_remove = [k for k in self._store if k[0] == repository_id]
            for k in keys_to_remove:
                del self._store[k]
            logger.info(
                "ReasoningCache invalidated %d entry/entries for repository_id=%r.",
                len(keys_to_remove),
                repository_id,
            )
            return len(keys_to_remove)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            count = len(self._store)
            self._store.clear()
            logger.info("ReasoningCache cleared %d entry/entries.", count)

    def size(self) -> int:
        """Return the current number of cached entries."""
        with self._lock:
            return len(self._store)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _evict(self) -> None:
        """Evict the oldest 10% of entries (FIFO order)."""
        evict_count = max(1, self._max_size // 10)
        keys = list(self._store.keys())[:evict_count]
        for k in keys:
            del self._store[k]
        logger.debug("ReasoningCache evicted %d old entry/entries.", evict_count)
