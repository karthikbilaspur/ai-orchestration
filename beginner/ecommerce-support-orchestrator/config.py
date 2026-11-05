"""Central configuration for the support orchestrator."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "log.txt"

# Optional LLM settings. If ANTHROPIC_API_KEY is not set, rule-based mode is used.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")

# Below this confidence the conversation is escalated to a human agent.
CONFIDENCE_THRESHOLD = 0.5

TRACKING_URL = "https://track.example.com/{order_id}"
REFUND_POLICY = (
    "You can request a refund within 30 days of delivery for unused items in "
    "their original packaging. Once we receive the return, your refund is "
    "processed to the original payment method within 5-7 business days."
)
