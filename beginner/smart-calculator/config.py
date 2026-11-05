"""Central settings for the AI Smart Calculator."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
LOG_FILE = BASE_DIR / "log.txt"

# Override with the CLAUDE_MODEL environment variable if you like.
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 800
