"""Validate either a raw run directory or a trace-v1 directory.

PRD S5, "Validation is mandatory at three points":

  (1) "The producer checks every sample of `observation.jsonl` against the
      recorder's own declaration in `driving.meta.json` (dtype, shape,
      encoding, stage names) and refuses the run on the first mismatch,
      naming the block and the two values." -- `check_run` / `check_sample`.
  (2) "The loader in lab-ui checks every block's bytes against the
      manifest's block table ... before drawing anything." -- `check_trace_dir`:
      validates manifest.json against trace-v1.schema.json, then the whole
      neural.trace file's sha256 (`hashes.neural_trace`), then every
      block's own sha256.

This module implements both, and the CLI picks one automatically: a
directory whose `manifest.json` has `"magic": "trace-v1"` is checked as a
trace-v1 directory (2); anything else is checked as a raw run directory (1).

CLI:

    python -m lab_api.trace.check <target_dir>

Exits 0 and prints a one-line summary on success. Exits 1 and prints the
exact mismatch (block name, expected value, actual value) on the first
failure -- never a warning that scrolls by.

In run-directory mode, reads `observation.jsonl` one line at a time and
stops as soon as the file is exhausted or `--max-samples` is reached; it
never loads the whole file, so it is safe to run against a run directory
that a battery is still writing to.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import reference_decoder as rd


class CheckError(ValueError):
    """A sample, a block, or a whole file does not match its own declaration."""


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


def is_trace_v1_dir(target_dir: Path) -> bool:
    """True if `target_dir/manifest.json` exists and declares `"magic": "trace-v1"`.

    A raw run directory also has a `manifest.json` (written by
    `universe_run.py`, with keys like `id`/`written`/`script`), which does
    NOT have a `magic` key -- this is what tells the two apart.
    """
    manifest_path = target_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    try:
        with open(manifest_path) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False
    return isinstance(data, dict) and data.get("magic") == "trace-v1"


def check_trace_dir(trace_dir: Path) -> dict:
    """Validates a trace-v1 directory: schema, then neural.trace integrity.

    Steps, in order (PRD S5 validation point 2):
      1. `manifest.json` validates against `trace-v1.schema.json`
         (`reference_decoder.load_manifest`, which also checks
         samples_tick length and per-block shape[0]/length consistency).
      2. Every block's own byte range `[offset, offset+length)` hashes to
         its declared `sha256` -- checked block-by-block, in manifest
         order, so a corruption inside a block's range is reported with
         that block's name (not just "the file changed somewhere").
      3. The whole `neural.trace` file's sha256 matches
         `manifest['hashes']['neural_trace']` -- a backstop for corruption
         that lands outside every block's declared range (e.g. in trailing
         padding); only reached if every individual block already matched.

    Returns the manifest. Raises CheckError naming the block/file and both
    hashes on the first mismatch.
    """
    try:
        manifest = rd.load_manifest(trace_dir)
    except rd.ManifestValidationError as exc:
        raise CheckError(f"manifest.json failed schema validation: {exc}") from exc

    trace_path = trace_dir / "neural.trace"
    if not trace_path.exists():
        raise CheckError(f"{trace_path} does not exist")
    trace_bytes = trace_path.read_bytes()

    for block in manifest["blocks"]:
        start, length = block["offset"], block["length"]
        chunk = trace_bytes[start:start + length]
        _expect(
            len(chunk) == length,
            f"block {block['name']!r}: expected {length} bytes at offset {start}, neural.trace has {len(chunk)}",
        )
        actual = hashlib.sha256(chunk).hexdigest()
        _expect(
            actual == block["sha256"],
            f"block {block['name']!r}: manifest sha256={block['sha256']}, actual sha256={actual}",
        )

    expected_whole = manifest["hashes"]["neural_trace"]
    actual_whole = hashlib.sha256(trace_bytes).hexdigest()
    _expect(
        actual_whole == expected_whole,
        f"neural.trace (whole file, every individual block matched -- corruption is outside any "
        f"declared block range): manifest hashes.neural_trace={expected_whole}, actual sha256={actual_whole}",
    )

    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m lab_api.trace.check",
        description=(
            "Validate either a run directory (observation.jsonl vs driving.meta.json) "
            "or a trace-v1 directory (manifest.json + neural.trace integrity), "
            "auto-detected by manifest.json's 'magic' field."
        ),
    )
    parser.add_argument(
        "target_dir", type=Path,
        help="run directory OR trace-v1 directory",
    )
    parser.add_argument("--max-samples", type=int, default=None, help="run-directory mode only: stop after this many samples (default: all)")
    args = parser.parse_args(argv)

    try:
        if is_trace_v1_dir(args.target_dir):
            manifest = check_trace_dir(args.target_dir)
            print(
                f"OK: manifest.json and {len(manifest['blocks'])} blocks in "
                f"{args.target_dir}/neural.trace match their declared sha256"
            )
        else:
            checked = check_run(args.target_dir, max_samples=args.max_samples)
            print(f"OK: {checked} samples in {args.target_dir}/observation.jsonl match {args.target_dir}/driving.meta.json")
    except CheckError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
