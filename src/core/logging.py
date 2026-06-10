import logging
import structlog

def setup_logging(log_level: int = logging.INFO) -> None:
    """Configure structlog with basic settings."""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=log_level)
    # Suppress verbose watchfiles main/reload logs
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a bound structlog logger."""
    return structlog.get_logger(name)
