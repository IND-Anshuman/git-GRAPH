import time
import uuid
from typing import Any, Iterator
import structlog
from contextlib import contextmanager

from src.core.logging import get_logger

def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())

class CorrelationIdMiddleware:
    """Middleware concept for correlation ID."""
    # In a real app this would hook into request/response lifecycle
    pass

@contextmanager
def TimingContext(operation_name: str, logger: structlog.BoundLogger | None = None) -> Iterator[None]:
    """Context manager that logs execution duration."""
    if logger is None:
        logger = get_logger(__name__)
        
    start_time = time.perf_counter()
    logger.debug(f"Starting {operation_name}")
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        logger.info(f"Completed {operation_name}", duration_sec=round(duration, 4))
