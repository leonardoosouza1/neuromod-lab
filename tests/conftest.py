"""Puts <repo>/src on sys.path so `python -m pytest` finds lab_api without
requiring PYTHONPATH to be set manually. See TESTING.md.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
