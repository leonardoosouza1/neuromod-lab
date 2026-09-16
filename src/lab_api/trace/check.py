"""Validate a run's `observation.jsonl` against its own `driving.meta.json`.

PRD S5, "Validation is mandatory at three points": point (1) is "The
producer checks every sample of `observation.jsonl` against the recorder's
own declaration in `driving.meta.json` (dtype, shape, encoding, stage names)
and refuses the run on the first mismatch, naming the block and the two
values." This module is that check, standalone so it can run as a
guard before the S2 producer builds a trace, and so `lab-ui up` can run it
before opening a run (PRD S5, validation point 3).

CLI:

    python -m lab_api.trace.check <run_dir>

Exits 0 and prints a one-line summary on success. Exits 1 and prints the
exact mismatch (block name, expected value, actual value, sample index and
tick) on the first failure -- never a warning that scrolls by.

Reads `observation.jsonl` one line at a time and stops as soon as the file
is exhausted or `--max-samples` is reached; it never loads the whole file,
so it is safe to run against a run directory that a battery is still
writing to.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class CheckError(ValueError):
    """A sample does not match the run's own driving.meta.json declaration."""


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def check_sample(sample: dict, meta: dict, index: int) -> None:
    """Validates one parsed observation.jsonl line against driving.meta.json.

    Raises CheckError naming the block and the two values on the first
    mismatch.
    """
    tick = sample.get("tick")
    rows = meta["retina_rows"]
    cols = meta["retina_cols"]
    expected_retina_len = rows * cols
    retina = sample.get("retina")
    _expect(
        isinstance(retina, list) and len(retina) == expected_retina_len,
        f"sample {index} (tick={tick}): block 'retina' has "
        f"{len(retina) if isinstance(retina, list) else type(retina).__name__} elements, "
        f"driving.meta.json declares retina_rows*retina_cols={rows}*{cols}={expected_retina_len}",
    )
    for j, value in enumerate(retina):
        _expect(
            isinstance(value, int) and 0 <= value <= 0xFFFFFFFF,
            f"sample {index} (tick={tick}): block 'retina' element {j}={value!r} is not a valid u32 "
            f"(driving.meta.json retina_encoding={meta.get('retina_encoding')!r})",
        )

    wave_channels = meta["wave_channels"]
    wave = sample.get("wave")
    _expect(
        isinstance(wave, list) and len(wave) == wave_channels,
        f"sample {index} (tick={tick}): block 'wave' has "
        f"{len(wave) if isinstance(wave, list) else type(wave).__name__} elements, "
        f"driving.meta.json declares wave_channels={wave_channels}",
    )
    for j, value in enumerate(wave):
        _expect(
            isinstance(value, int) and -128 <= value <= 127,
            f"sample {index} (tick={tick}): block 'wave' element {j}={value!r} is not a valid i8",
        )

    fast_values = meta["fast_state_values"]
    fast_state = sample.get("fast_state")
    if fast_state is not None:
        _expect(
            isinstance(fast_state, list) and len(fast_state) == fast_values,
            f"sample {index} (tick={tick}): block 'fast_state' (declared stage "
            f"{meta.get('fast_state_stage')!r}) has "
            f"{len(fast_state) if isinstance(fast_state, list) else type(fast_state).__name__} elements, "
            f"driving.meta.json declares fast_state_values={fast_values}",
        )
        _expect(
            all(isinstance(v, (int, float)) and v == v and abs(v) != float("inf") for v in fast_state),
            f"sample {index} (tick={tick}): block 'fast_state' contains a non-finite value",
        )

    body = sample.get("body")
    _expect(isinstance(body, dict), f"sample {index} (tick={tick}): 'body' is missing or not an object")
    motor_trace = body.get("motor_trace") if isinstance(body, dict) else None
    if motor_trace is not None:
        expected_stage = meta.get("motor_trace_phase")
        actual_stage = motor_trace.get("phase")
        _expect(
            expected_stage is None or actual_stage == expected_stage,
            f"sample {index} (tick={tick}): body.motor_trace.phase={actual_stage!r}, "
            f"driving.meta.json declares motor_trace_phase={expected_stage!r}",
        )


def check_run(run_dir: Path, max_samples: int | None = None) -> int:
    """Validates observation.jsonl against driving.meta.json for `run_dir`.

    Returns the number of samples checked. Raises CheckError on the first
    mismatch (naming the block and the two values, per PRD S5).
    """
    meta_path = run_dir / "driving.meta.json"
    if not meta_path.exists():
        raise CheckError(f"{meta_path} does not exist -- was --driving-diagnostics used for this run?")
    with open(meta_path) as f:
        meta = json.load(f)

    for required_key in ("retina_rows", "retina_cols", "wave_channels", "fast_state_values"):
        if required_key not in meta:
            raise CheckError(f"{meta_path} is missing required key {required_key!r}")

    obs_path = run_dir / "observation.jsonl"
    if not obs_path.exists():
        raise CheckError(f"{obs_path} does not exist")

    checked = 0
    prev_tick = None
    with open(obs_path) as f:
        for index, line in enumerate(f):
            if max_samples is not None and index >= max_samples:
                break
            line = line.strip()
            if not line:
                continue
            try:
                sample = json.loads(line)
            except json.JSONDecodeError as exc:
                if index == checked:
                    # Could be a partial last line from a writer still appending.
                    break
                raise CheckError(f"sample {index}: invalid JSON ({exc})") from exc
            check_sample(sample, meta, index)
            tick = sample.get("tick")
            if prev_tick is not None:
                _expect(
                    isinstance(tick, int) and tick > prev_tick,
                    f"sample {index}: tick {tick} does not increase over the previous sample's tick {prev_tick}",
                )
            prev_tick = tick
            checked += 1
    return checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m lab_api.trace.check",
        description="Validate <run_dir>/observation.jsonl against <run_dir>/driving.meta.json.",
    )
    parser.add_argument("run_dir", type=Path, help="run directory (contains observation.jsonl and driving.meta.json)")
    parser.add_argument("--max-samples", type=int, default=None, help="stop after this many samples (default: all)")
    args = parser.parse_args(argv)

    try:
        checked = check_run(args.run_dir, max_samples=args.max_samples)
    except CheckError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {checked} samples in {args.run_dir}/observation.jsonl match {args.run_dir}/driving.meta.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
