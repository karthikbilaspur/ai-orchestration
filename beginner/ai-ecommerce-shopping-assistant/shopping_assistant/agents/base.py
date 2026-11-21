"""Shared base class so every agent has a name and a logger."""
from __future__ import annotations

import logging
from typing import Optional


class BaseAgent:
    name = "Agent"

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.log = logger or logging.getLogger(f"shopping_assistant.{self.name}")

    def run(self, *args, **kwargs):  # pragma: no cover - overridden by subclasses
        raise NotImplementedError
