"""Logging set-up: every agent step is written to a log file (log.txt)."""
from __future__ import annotations

import logging
import sys

ROOT_LOGGER_NAME = "shopping_assistant"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(log_path: str = "log.txt", level: int = logging.INFO,
                  console: bool = False, mode: str = "w") -> logging.Logger:
    """Send all assistant logs to `log_path` (and optionally the console).

    Calling it twice replaces the old handlers, so you never get duplicate lines.
    """
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(log_path, mode=mode, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if console:
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(formatter)
        logger.addHandler(stream)
    return logger
