"""Allow ``python -m meeting_assistant``."""
import sys

from meeting_assistant.cli import main

if __name__ == "__main__":
    sys.exit(main())
