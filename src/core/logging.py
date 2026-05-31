"""
Structured Logging Setup.
Configures structlog for JSON logs in production and readable formatting in development.
"""

import logging
import sys
import structlog

from src.config import settings


def setup_logging() -> None:
    """Configures structured logging for the entire platform."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.environment == "local":
        # Interactive colored output for local CLI console
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # Standard structural JSON logs for log shippers (ELK / Grafana Loki)
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.debug else logging.INFO
        ),
        cache_logger_on_first_use=True,
    )

    # Route standard Python stdlib logging through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
