import re
import logging
import sys
from app.core.config import settings

class SensitiveDataFilter(logging.Filter):
    """
    Log filter that redacts passwords, JWT tokens, API keys, and credentials
    from all application log records.
    """
    SENSITIVE_PATTERNS = [
        (re.compile(r'("password"|"hashed_password"|"password_hash"|"secret")\s*:\s*["\'][^"\']+["\']', re.IGNORECASE), r'\1: "***REDACTED***"'),
        (re.compile(r'(Bearer\s+)[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', re.IGNORECASE), r'\1***JWT_REDACTED***'),
        (re.compile(r'(X-API-Key:\s*)[^\s]+', re.IGNORECASE), r'\1***API_KEY_REDACTED***'),
        (re.compile(r'(postgresql://[^:]+:)[^@]+(@)', re.IGNORECASE), r'\1***PASSWORD_REDACTED***\2'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        if record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                new_args.append(arg)
            record.args = tuple(new_args)
        return True

def setup_logging():
    """
    Initializes structured application logging.
    Sets log level from settings.LOG_LEVEL and attaches SensitiveDataFilter.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to prevent duplicate log lines
    root_logger.handlers = [handler]

    # Configure specific loggers
    for logger_name in ["fastapi_backend", "mqtt_client", "tracking_service", "auth_service"]:
        l = logging.getLogger(logger_name)
        l.setLevel(log_level)

    logger = logging.getLogger("fastapi_backend")
    logger.info(f"Logging initialized at level '{settings.LOG_LEVEL.upper()}' (Environment: '{settings.APP_ENV}')")
