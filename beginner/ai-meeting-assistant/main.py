"""Entry point: ``python main.py`` (interactive) or ``python main.py --help``."""
import sys

from meeting_assistant.cli import main

if __name__ == "__main__":
    sys.exit(main())
