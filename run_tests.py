#!/usr/bin/env python3
"""
Test runner script for the High School Management System.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests with coverage."""
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("Virtual environment not found. Please run 'python -m venv .venv' first.")
        sys.exit(1)
    
    # Run tests with coverage
    cmd = [
        str(venv_python),
        "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    print("Running tests with coverage...")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()