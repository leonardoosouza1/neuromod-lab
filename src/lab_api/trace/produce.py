"""CLI for the trace-v1 producer (lab-ui PRD S2 item 5).

    cd <repo>/src && PYTHONPATH=. python -m lab_api.trace.produce <run_dir> --gen N \\
        [--being B] [--profile summary|champion|event|full] [--force] \\
        [--db PATH | --no-db]

    cd <repo>/src && PYTHONPATH=. python -m lab_api.trace.produce --all-finished <runs_root> \\
        [--db PATH | --no-db] [--force]

`--all-finished` produces the CHAMPION-profile trace of the LAST generation for every
run under `runs_root` that (a) has an `observation.jsonl` and (b) is finished --
`gens_complete >= gens_requested`, the same definition `lab_db.ingest_run` uses, via
counting `population_gen*.json` files against `manifest.json`'s `args.gens`. This is
also exactly what keeps it from ever touching a run still being written: an in-flight
run has fewer `population_gen*.json` files than requested, so it is skipped, not raced.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import producer as trace_producer


def _is_finished(run_dir: Path) -> tuple[bool, int | None]:
    """Returns (finished, last_generation_index)."""
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return False, None
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        return False, None
    args = manifest.get("args", {}) or {}
    requested = int(args.get("gens", 0) or 0)
    gens = sorted(
        int(p.stem.replace("population_gen", ""))
        for p in run_dir.glob("population_gen*.json")
    )
    if not gens:
        return False, None
    complete = len(gens)
    finished = requested > 0 and complete >= requested
    return finished, gens[-1]


def _produce_one(run_dir: Path, gen: int, being, profile: str, force: bool, db_path: str | None) -> int:
    try:
        trace_dir = trace_producer.produce(run_dir, gen, being=being, profile=profile, force=force)
    except trace_producer.TraceUpToDate as exc:
        print(f"UP TO DATE: {exc.trace_dir} (use --force to rebuild)")
        trace_dir = exc.trace_dir
    except trace_producer.ProducerError as exc:
        print(f"FAIL {run_dir.name} gen={gen}: {exc}", file=sys.stderr)
        return 1

    if db_path is not None:
        trace_producer.register(trace_dir, db_path=db_path)
        print(f"OK: {trace_dir} (registered in {db_path})")
    else:
        print(f"OK: {trace_dir} (--no-db, not registered)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m lab_api.trace.produce",
        description="Produce a trace-v1 directory from a Universe run's observation.jsonl/replay/genome.",
    )
    parser.add_argument("run_dir", nargs="?", type=Path, help="run directory (omit with --all-finished)")
    parser.add_argument("--gen", type=int, help="generation index (required unless --all-finished)")
    parser.add_argument("--being", type=int, default=None, help="population slot (default: driving.meta.json's selected_being)")
    parser.add_argument("--profile", choices=("summary", "champion", "event", "full"), default="champion")
    parser.add_argument("--force", action="store_true", help="rebuild even if source hashes still match")
    parser.add_argument("--db", default=None, help="lab.db path (default: lab_db.DEFAULT_PATH)")
    parser.add_argument("--no-db", action="store_true", help="skip trace registration entirely")
    parser.add_argument("--all-finished", type=Path, default=None, metavar="RUNS_ROOT",
                         help="produce the champion trace of the last generation for every finished run under RUNS_ROOT")
    args = parser.parse_args(argv)

    db_path = None if args.no_db else (args.db or trace_producer.lab_db.DEFAULT_PATH)

    if args.all_finished is not None:
        runs_root = args.all_finished
        if not runs_root.is_dir():
            print(f"FAIL: {runs_root} is not a directory", file=sys.stderr)
            return 1
        candidates = sorted(
            d for d in runs_root.iterdir()
            if d.is_dir() and (d / "observation.jsonl").exists()
        )
        if not candidates:
            print(f"no run under {runs_root} has an observation.jsonl")
            return 0
        exit_code = 0
        n_produced = 0
        n_skipped = 0
        for run_dir in candidates:
            finished, last_gen = _is_finished(run_dir)
            if not finished:
                n_skipped += 1
                print(f"SKIP {run_dir.name}: not finished (or no population_gen*.json yet)")
                continue
            rc = _produce_one(run_dir, last_gen, None, "champion", args.force, db_path)
            if rc != 0:
                exit_code = rc
            else:
                n_produced += 1
        print(f"--all-finished: {n_produced} produced, {n_skipped} skipped (not finished), out of {len(candidates)} candidates")
        return exit_code

    if args.run_dir is None or args.gen is None:
        parser.error("run_dir and --gen are required unless --all-finished is given")

    return _produce_one(args.run_dir, args.gen, args.being, args.profile, args.force, db_path)


if __name__ == "__main__":
    raise SystemExit(main())
