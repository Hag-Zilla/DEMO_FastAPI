"""Logging configuration for the application."""

import logging
from logging.config import dictConfig
from pathlib import Path

import yaml

from app.core.config import settings


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

    if getattr(root_logger, "_expense_tracker_configured", False):
        return

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    log_level = "DEBUG" if settings.DEBUG else "INFO"
    config_path = Path("config/logging.yaml")

    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as config_file:
            logging_config = yaml.safe_load(config_file)
    else:
        logging_config = _default_logging_config(log_level)

    logging_config["root"]["level"] = log_level
    if "console" in logging_config.get("handlers", {}):
        logging_config["handlers"]["console"]["level"] = log_level
    if "file" in logging_config.get("handlers", {}):
        logging_config["handlers"]["file"]["level"] = log_level

    dictConfig(logging_config)
    root_logger._expense_tracker_configured = True


configure_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__).

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)
