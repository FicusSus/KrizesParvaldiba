"""
Logging Configuration

This module sets up structured logging using structlog.
It provides colored console output and JSON logging for production.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog


def setup_logging():
    """
    Setup structured logging for the application.
    
    Configures:
    - Console logging with colors in development
    - JSON logging in production
    - File logging for persistence
    """
    from app.core.config import settings
    
    # Shared processors for all loggers
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.DEBUG:
        # Development: colored console output
        console_processors = shared_processors + [
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Production: JSON output
        console_processors = shared_processors + [
            structlog.processors.JSONRenderer(),
        ]
    
    # File processors: always JSON
    file_processors = shared_processors + [
        structlog.processors.JSONRenderer(),
    ]
    
    # Configure structlog
    structlog.configure(
        processors=console_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging to redirect to structlog
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        handlers=[
            structlog.stdlib.Handler(),
        ],
        format="%(message)s",
    )
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler
    file_handler = logging.FileHandler(
        filename=settings.LOG_FILE,
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    ))
    
    # Get root logger and add file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Set log level for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a named logger with context.
    
    Args:
        name: Logger name (usually __name__).
        
    Returns:
        structlog.BoundLogger: Configured logger.
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding context to logs.
    """
    
    def __init__(self, logger: structlog.BoundLogger, **context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self._original_context = {}
    
    def __enter__(self):
        self._original_context = self.logger._context.copy()
        self.logger = self.logger.bind(**self.context)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original context
        self.logger = self.logger.bind(**self._original_context)
