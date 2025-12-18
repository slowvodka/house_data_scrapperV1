"""
Entry point for running CLI as a module: python -m src.cli
"""

from src.cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())

