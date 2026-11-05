"""Central configuration for the job application screener."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "log.txt"
OUTPUT_DIR = BASE_DIR / "output"

# Optional LLM settings. Without ANTHROPIC_API_KEY the rule-based mode is used.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

DEFAULT_JD = "Need Python + AI/LLM intern"

# Decision thresholds (score is 1-10)
SHORTLIST_SCORE = 7      # strong match at or above this -> Shortlisted
REVIEW_SCORE = 5         # at or above this -> human review, below -> Rejected
WEAK_MATCH_CAP = 5       # a Weak Match can never score above this
