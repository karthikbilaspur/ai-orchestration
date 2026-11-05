"""Central configuration for the expense checker."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "log.txt"
OUTPUT_DIR = BASE_DIR / "output"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")   # optional, Parser fallback only
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

# ---- Company policy (Rs) -------------------------------------------------
BILL_REQUIRED_ABOVE = 1000     # Rule 1: amount > 1000 and no bill -> Rejected
AUTO_APPROVE_BELOW = 500       # Rule 2: amount < 500 -> Approved

# Extra safety rule (not in the original task): above the bill limit with NO information
# about a bill, ask the employee instead of silently sending it on to the manager.
# Set to False for the strict 3-rule behaviour.
ASK_WHEN_BILL_UNKNOWN = True
