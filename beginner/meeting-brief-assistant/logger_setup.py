"""Logging to both console and log.txt (thread name included to show parallelism)."""
import logging
from config import LOG_FILE


def get_logger(name: str = "briefing") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s.%(msecs)03d | %(threadName)-10s | %(message)s",
                            "%H:%M:%S")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(console)
    logger.propagate = False
    return logger
