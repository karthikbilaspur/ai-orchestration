"""Logging configuration: everything the pipeline does is written to log.txt."""
from __future__ import annotations

import logging
from pathlib import Path

LOGGER_NAME = "study_planner"
_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(log_path, level=logging.INFO) -> logging.Handler:
    """Attach a file handler to the package logger and return it."""
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(_FORMAT))
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(handler)
    return handler


def teardown_logging(handler: logging.Handler) -> None:
    logging.getLogger(LOGGER_NAME).removeHandler(handler)
    handler.close()
