"""Logging configuration for the application."""

# ============================================================================
# IMPORTS
# ============================================================================

import json
import logging
import re
from datetime import datetime, timezone
from logging.config import dictConfig
from pathlib import Path

import yaml

from app.core.config import settings


# ============================================================================
# CONFIGURATION / CONSTANTS
# ============================================================================

_URL_CREDENTIALS_RE = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://)([^:/\s]+):([^@/\s]+)@")
_SECRET_PAIR_RE = re.compile(
    r"(?i)\b(SECRET_KEY|PASSWORD|TOKEN|API_KEY|AUTHORIZATION)\b\s*([=:])\s*([^\s,;]+)"
)


# ============================================================================
# PRIVATE HELPERS
# ============================================================================


def _redact_text(value: str) -> str:
    """Mask common sensitive patterns in log text."""
    redacted = _URL_CREDENTIALS_RE.sub(r"\1\2:***@", value)
    redacted = _SECRET_PAIR_RE.sub(r"\1\2***", redacted)
    return redacted


def _redact_obj(value):
    """Recursively redact strings nested inside logging arguments."""
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, tuple):
        return tuple(_redact_obj(item) for item in value)
    if isinstance(value, list):
        return [_redact_obj(item) for item in value]
    if isinstance(value, dict):
        return {k: _redact_obj(v) for k, v in value.items()}
    return value


# ============================================================================
# PUBLIC CLASSES
# ============================================================================


class SafeFormatter(logging.Formatter):
    """Formatter that redacts sensitive values from messages and tracebacks."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with sensitive data redaction.

        Args:
            record: The log record to format.

        Returns:
            The formatted log string with sensitive values masked.
        """
        original_msg = record.msg
        original_args = record.args
        try:
            if isinstance(record.msg, str):
                record.msg = _redact_text(record.msg)
            if record.args:
                record.args = _redact_obj(record.args)
            return super().format(record)
        finally:
            record.msg = original_msg
            record.args = original_args

    def formatException(self, ei) -> str:  # noqa: N802 - stdlib API naming
        """Format exception information with sensitive data redaction.

        Args:
            ei: The exception info tuple.

        Returns:
            The formatted exception string with sensitive values masked.
        """
        return _redact_text(super().formatException(ei))


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON line."""
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "logger": record.name,
            "level": record.levelname,
            "message": _redact_text(record.getMessage()),
        }

        # Add extra fields if present
        if hasattr(record, "http_method"):
            log_data["http_method"] = record.http_method
        if hasattr(record, "http_path"):
            log_data["http_path"] = record.http_path
        if hasattr(record, "http_status"):
            log_data["http_status"] = record.http_status
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = _redact_text(self.formatException(record.exc_info))

        return json.dumps(log_data, ensure_ascii=False)


# ============================================================================
# MODULE SETUP / CONFIGURATION
# ============================================================================


def _default_logging_config(log_level: str) -> dict:
    """Return fallback logging config when YAML file is unavailable."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "standard",
                "filename": "logs/app.log",
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"],
        },
    }


def configure_logging() -> None:
    """Configure application logging once on the root logger."""
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_level = "DEBUG" if settings.DEBUG else "INFO"
    # prefer project-level logs/config/logging.yaml
    config_path = Path("logs/config/logging.yaml")

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as config_file:
            logging_config = yaml.safe_load(config_file)
    else:
        logging_config = _default_logging_config(log_level)

    # Inject JSONFormatter class to avoid circular import issues
    if "standard" in logging_config.get("formatters", {}):
        logging_config["formatters"]["standard"]["()"] = SafeFormatter

    # Inject JSONFormatter class to avoid circular import issues
    if "json" in logging_config.get("formatters", {}):
        logging_config["formatters"]["json"]["()"] = JSONFormatter

    dictConfig(logging_config)


configure_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
