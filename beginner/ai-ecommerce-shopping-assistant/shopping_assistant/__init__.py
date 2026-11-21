"""AI E-commerce Shopping Assistant - a four-agent product discovery demo."""
import logging

from .catalog import Catalog, load_default_catalog
from .models import SessionResult
from .orchestrator import ShoppingAssistant

__all__ = ["ShoppingAssistant", "Catalog", "load_default_catalog", "SessionResult"]
__version__ = "1.0.0"

# Stay silent unless the application (e.g. main.py) configures logging.
logging.getLogger("shopping_assistant").addHandler(logging.NullHandler())
