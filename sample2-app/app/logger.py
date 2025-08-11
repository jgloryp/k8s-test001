import structlog
import os
import sys
from typing import Any, Dict

def configure_logging() -> structlog.BoundLogger:
    environment = os.getenv('ENVIRONMENT', 'development')
    log_level = os.getenv('LOG_LEVEL', 'info').upper()
    
    processors = [
        structlog.processors.TimeStamper(fmt="YYYY-MM-DD HH:mm:ss"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if environment == 'development':
        processors.extend([
            structlog.dev.ConsoleRenderer()
        ])
    else:
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger()
    logger = logger.bind(
        service="sample2-app",
        environment=environment
    )
    
    return logger

logger = configure_logging()