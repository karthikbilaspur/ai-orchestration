"""Writes every pipeline step to log.txt."""
import logging

from config import LOG_FILE


def get_logger(name: str = "smart_calculator") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:  # already configured
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger
