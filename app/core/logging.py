"""Logging configuration for the application."""

import json
import logging
from datetime import datetime, timezone
from logging.config import dictConfig
from pathlib import Path

import yaml

from app.core.config import settings


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
            "message": record.getMessage(),
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
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


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
