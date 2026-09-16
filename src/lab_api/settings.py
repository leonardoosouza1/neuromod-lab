"""Runtime configuration for the lab-ui API (PRD S1).

A plain pydantic `BaseModel`, not `pydantic_settings.BaseSettings` -- the
task's `--no-deps` pin list does not include `pydantic-settings`, and this
module's job (parse argv, read one env file under `--lan`, apply defaults)
is small enough that pulling in a second package for it would be exactly
the kind of dependency creep the pin list exists to prevent.

Precedence, low to high: hardcoded default -> `--lan`'s env file
(`LAB_UI_PASSWORD` only) -> CLI flag.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_DB = "/media/llm-data/lab.db"
DEFAULT_RUNS_ROOT = "/media/llm-data/universe-runs/neuromod-lab-taxi"
DEFAULT_SPOOL = "/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd"
DEFAULT_SNAPSHOTS_ROOT = "/media/llm-data/snapshots"
DEFAULT_UNIVERSE_ROOT = os.path.expanduser("~/projects/LLM/Universe")
DEFAULT_ENV_FILE = "/media/llm-data/lab-ui.env"
DEFAULT_PORT = 8130


class Settings(BaseModel):
    """Everything a route or `auth.py` needs to know about how this process was started."""

    db: str = DEFAULT_DB
    runs_root: str = DEFAULT_RUNS_ROOT
    spool: str = DEFAULT_SPOOL
    snapshots_root: str = DEFAULT_SNAPSHOTS_ROOT
    universe_root: str = DEFAULT_UNIVERSE_ROOT
    bind: str = "127.0.0.1"
    port: int = DEFAULT_PORT
    lan: bool = False
    # Only set (and only required) when lan=True. Never logged, never echoed by any
    # route -- see auth.py's own docstring for why.
    password: str | None = Field(default=None, repr=False)

    model_config = {"frozen": True}


def _read_env_file(path: str) -> dict[str, str]:
    """Parses a minimal `KEY=VALUE` file, one assignment per line. No quoting, no
    interpolation, no dependency on `python-dotenv` -- the env file this project
    writes (per PRD S1 §8: "created on first start, never in repo/chat/docs") only
    ever needs to carry `LAB_UI_PASSWORD`, so a full dotenv parser is not warranted.
    Blank lines and lines starting with `#` are skipped.
    """
    values: dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return values
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_settings(argv: list[str] | None = None) -> Settings:
    """Parses CLI args (see `__main__.py`) into a `Settings`. Under `--lan`, reads the
    password from `env_file` (default `/media/llm-data/lab-ui.env`) and REFUSES to
    build settings when it is missing -- PRD S1 §8: "--lan binds 0.0.0.0, REQUIRES the
    password ... refuse to start if missing; never generate, never log it."
    """
    ap = argparse.ArgumentParser(prog="lab_api", description="lab-ui API server")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--bind", default=None, help="override the bind address directly")
    ap.add_argument("--lan", action="store_true", help="bind 0.0.0.0 and require a password")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT)
    ap.add_argument("--spool", default=DEFAULT_SPOOL)
    ap.add_argument("--snapshots-root", default=DEFAULT_SNAPSHOTS_ROOT)
    ap.add_argument("--universe-root", default=DEFAULT_UNIVERSE_ROOT)
    ap.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    a = ap.parse_args(argv)

    bind = a.bind or ("0.0.0.0" if a.lan else "127.0.0.1")
    password = None
    if a.lan:
        env = _read_env_file(a.env_file)
        password = env.get("LAB_UI_PASSWORD")
        if not password:
            raise SystemExit(
                f"--lan requires LAB_UI_PASSWORD in {a.env_file!r}; this process never "
                "generates one -- create the file by hand (PRD S1 §8) and retry"
            )

    return Settings(
        db=a.db, runs_root=a.runs_root, spool=a.spool, snapshots_root=a.snapshots_root,
        universe_root=a.universe_root, bind=bind, port=a.port, lan=a.lan, password=password,
    )
