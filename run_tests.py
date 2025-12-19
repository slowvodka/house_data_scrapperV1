#!/usr/bin/env python
"""Convenience script to run different test groups.

Usage:
    python run_tests.py calculator    # Run calculator tests only
    python run_tests.py scraper       # Run scraper tests only
    python run_tests.py all           # Run all tests
    python run_tests.py               # Show help
"""
import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable commands:")
        print("  calculator - Run mortgage calculator tests (no external deps)")
        print("  scraper    - Run scraper tests (requires pyarrow, responses)")
        print("  all        - Run all tests")
        return 0
    
    command = sys.argv[1].lower()
    
    if command == "calculator":
        print("Running calculator tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_mortgage_calculator/",
            "-v", "--tb=short"
        ])
        return result.returncode
    
    elif command == "scraper":
        print("Running scraper tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "--ignore=tests/test_mortgage_calculator/",
            "-v", "--tb=short"
        ])
        return result.returncode
    
    elif command == "all":
        print("Running all tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v", "--tb=short"
        ])
        return result.returncode
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'calculator', 'scraper', or 'all'")
        return 1


if __name__ == "__main__":
    sys.exit(main())

