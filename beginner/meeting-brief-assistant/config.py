"""Central configuration for the meeting brief assistant."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "log.txt"
OUTPUT_DIR = BASE_DIR / "output"

# Optional LLM settings. Without ANTHROPIC_API_KEY everything runs offline.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

AGENT_TIMEOUT = 20          # seconds to wait for each parallel agent
MAX_BRIEF_LINES = 45        # the cheat-sheet must stay a 1-page read

# Seconds each agent "waits" to imitate a slow search/LLM call, so the log shows
# the parallel speed-up. Set SIMULATED_LATENCY=0 to switch it off.
SIMULATED_LATENCY = float(os.getenv("SIMULATED_LATENCY", "0.5"))
