"""Puts <repo>/src on sys.path so `python -m pytest` finds lab_api without
requiring PYTHONPATH to be set manually. See TESTING.md.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def find_lab_ui() -> Path:
    """The lab-ui checkout is a sibling of this repository in the main layout
    (`LLM/neuromod-lab` next to `LLM/lab-ui`) and two levels up from a slice worktree
    (`LLM/.worktrees/<slice>`). Resolving only one of the two made the contract suites skip
    silently on the other (16/09, twice). `LAB_UI_REPO` wins when set."""
    import os
    repo_root = Path(__file__).resolve().parents[1]
    if "LAB_UI_REPO" in os.environ:
        return Path(os.environ["LAB_UI_REPO"])
    for candidate in (repo_root.parent / "lab-ui", repo_root.parents[1] / "lab-ui"):
        if (candidate / "contract").is_dir():
            return candidate
    return repo_root.parent / "lab-ui"
