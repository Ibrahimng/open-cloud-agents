"""
Open Cloud Agents: Module execution entry point.
Enables running the CLI via: python -m ocagents
"""
import sys
from ocagents.cli import main

if __name__ == "__main__":
    sys.exit(main())
