"""Allow ``python -m study_planner``."""
import sys

from study_planner.cli import main

if __name__ == "__main__":
    sys.exit(main())
