"""lab-ui PRD S2 -- the trace-v1 producer.

`produce(run_dir, gen, being=None, profile='champion')` reads one generation's
`observation.jsonl` rows for one being, the generation's `physical.replay` and
`evolve_best_gen<NNNN>.bin`, and writes the trace-v1 directory PRD S5 defines:
`manifest.json`, `neural.trace`, `events.json`, `track.json`, `weights.json`, and
symlinks `physical.replay` / `genome.bin`.

Contract documents this module codes against (read them first, they are not repeated
here): `lab-ui/PRD.md` §5, `lab-ui/contract/{REPLAY-FORMAT.md,EVENTS.md,DEVIATIONS.md}`,
`lab-ui/contract/trace-v1.schema.json`, and the S0 fixture
`lab-ui/fixtures/trace-v1/universe-b2-gen0/` (this producer's output for the SAME source
run/generation/being is expected to agree with that fixture on every shared block --
`tests/test_trace_producer.py` checks this when the b2 source is still on disk).

Genome/weights export and track export are NOT reimplemented here: this module shells
out to the Rust binaries `genome_export` and `track_export` (Universe worktree
`ui/s2-pack`, `Universe/src/bin/{genome_export,track_export}.rs`) -- the only place the
genome layout (`gpu/genome_io.rs`) and the track (`world::VoxelWorld`) are read.

Validation order (PRD S5, "Validation is mandatory"): `check.check_run` is called FIRST,
before any other read of `observation.jsonl` -- a mismatch against `driving.meta.json`
refuses the whole run, naming the block and the two values, exactly as `check.py` does
on its own.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

# `src/` (this file's great-grandparent) holds both `lab_api/` and `lab_db.py` as
# top-level siblings -- see tests/conftest.py and TESTING.md's `cd src && PYTHONPATH=.`
# convention, which this mirrors defensively so `producer.py` also works when imported
# from a process that started somewhere else.
_SRC_DIR = Path(__file__).resolve().parents[2]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import lab_db  # noqa: E402  (see sys.path shim above)

from . import check as trace_check  # noqa: E402
from . import reference_decoder as rd  # noqa: E402

SCHEMA_VERSION = 1
BODY_SCHEMA_VERSION = 1
BRAIN_SCHEMA_VERSION = 1

# gpu_evolve/cli_flags.rs -- the FOUR P1.7 control-arm flags (the trace-v1 schema's own
# prose names only 3 of these; the 4th, --no-neuron-period, is a real, separate flag --
# see src/lab_api/DEVIATIONS.md).
DISABLED_FLAG_NAMES = (
    "--no-neuron-memory",
    "--no-neuron-period",
    "--no-neuron-threshold",
    "--no-heterogeneous-activation",
)

# Where this task built genome_export/track_export (Universe worktree `ui/s2-pack`).
# Overridable so the same module works once these binaries live somewhere else (e.g.
# after S2 merges to main and a real build/install path exists).
DEFAULT_UNIVERSE_BIN_DIR = os.environ.get(
    "UNIVERSE_S2_BIN_DIR",
    "/home/leonardo/projects/LLM/.worktrees/universe-s2-pack/target/release",
)

# Blocks in the recorder's brain_flow execution order (PRD S5): sensor -> wave -> brain
# stage(s) -> motor chain -> pose/body. `l1`/`l2`/`intent` are the coarse SCHEMA-1
# placeholder names driving_diagnostics.rs never recorded at all -- always listed in
# `absent` for a schema-1 (or missing `observation_schema`) run. A schema-2 run
# (Universe/docs/KERNELS-OBSERVATION-L1L2.md) replaces this coarse placeholder with nine
# real, finer-grained stage blocks (`_STAGE2_BLOCK_NAMES` below); a schema-2 trace does
# NOT also emit these three coarse absence entries -- they were never real block
# identifiers, just a marker for "not implemented yet", and schema-2 supersedes them.
_NEVER_RECORDED_STAGES = (
    ("l1", "not recorded by this binary"),
    ("l2", "not recorded by this binary"),
    ("intent", "not recorded by this binary"),
)

# The four motor_trace-derived blocks (PRD S5) -- absent together when no sample in
# range carries `body.motor_trace` (see `_sample_has_motor_trace`).
_MOTOR_BLOCK_NAMES = frozenset({"raw_intent", "after_head", "after_modulation", "final_command"})

# Universe/docs/KERNELS-OBSERVATION-L1L2.md §3/§5 -- the nine exact stage arrays a
# schema-2 recording adds to observation.jsonl's `stages` object. `cfc_state` is
# deliberately NOT one of these: it duplicates the existing legacy `cfc`/`fast_state`
# block byte-for-byte (the doc's §2: "a second field ... would duplicate data and hide
# the stages before it"; §5: "Keep `fast_state` for schema-v1 readers and write
# `stages.cfc_state` with the same values"). Absent together when no sample in range
# carries `stages` (see `_sample_has_stages`) or when `driving.meta.json` does not
# declare `observation_schema: 2`.
_STAGE2_BLOCK_NAMES = frozenset({
    "l1_matmul", "l1_effective", "l1_to_l2",
    "l2_matmul", "l2_effective", "l2_std",
    "l2_adapted", "bypass_adapted", "final_intent",
})


class ProducerError(ValueError):
    """A run, generation or being cannot be turned into a trace-v1 directory."""


class TraceUpToDate(Exception):
    """The existing trace_dir's manifest already matches every current source hash."""

    def __init__(self, trace_dir: Path):
        self.trace_dir = trace_dir
        super().__init__(f"{trace_dir} is already up to date (use force=True to rebuild)")


# ── small utilities ───────────────────────────────────────────────────────────────────

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _binary_path(name: str) -> str:
    candidate = Path(DEFAULT_UNIVERSE_BIN_DIR) / name
    if candidate.exists():
        return str(candidate)
    return name  # fall back to PATH -- lets a future "real" install work unmodified


def _run_binary(args: list[str], what: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ProducerError(
            f"{what} failed (exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc


def _read_json(path: Path) -> Any:
    with open(path) as f:
        return json.load(f)


# ── source reading ───────────────────────────────────────────────────────────────────

def _iter_generation_samples(run_dir: Path, gen: int, being: int) -> Iterable[dict]:
    """Yields parsed observation.jsonl rows for (gen, being), in file order (= tick order)."""
    obs_path = run_dir / "observation.jsonl"
    with open(obs_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("generation") == gen and row.get("being") == being:
                yield row


def _find_genome_path(run_dir: Path, gen: int) -> Path:
    path = run_dir / f"evolve_best_gen{gen:04d}.bin"
    if not path.exists():
        raise ProducerError(f"{path} does not exist -- generation {gen} has no saved champion genome")
    return path


def _find_replay_path(run_dir: Path, gen: int) -> Path:
    path = run_dir / f"gen{gen:04d}.replay"
    if not path.exists():
        raise ProducerError(f"{path} does not exist -- generation {gen} has no recorded replay")
    return path


def _being_selection_text(being: int, gen: int, meta: dict, run_manifest: dict) -> str:
    """Honest 'being_selection' text -- PRD S5 / contract/DEVIATIONS.md #2.

    Never says "champion" unless the run actually resumed from a checkpoint (the only
    condition under which population slot 0 is documented to be the prior generation's
    measured elite, `Universe/src/bin/gpu_evolve/main.rs` `elite_carregado_do_checkpoint`).
    """
    args = run_manifest.get("args", {}) or {}
    resumed = bool(args.get("resume"))
    selected = meta.get("selected_being")
    if being != selected:
        return (
            f"population_slot_{being} (NOT the recorder's own selected_being={selected} for this "
            f"run -- produced with an explicit --being override; no relationship to the fitness "
            f"champion is claimed or checked)"
        )
    if resumed:
        return (
            f"fixed_population_slot_{being} (--vision-being default; this run passed --resume, "
            f"so slot 0 is documented to be the PRIOR generation's measured elite -- "
            f"Universe/src/bin/gpu_evolve/main.rs elite_carregado_do_checkpoint -- but this producer "
            f"does not independently verify it against the genome hash; see contract/DEVIATIONS.md #2)"
        )
    return (
        f"fixed_population_slot_{being} (--vision-being default; this run did NOT pass --resume, "
        f"so slot {being} is NOT verified to be the fitness champion of generation {gen} -- "
        f"see contract/DEVIATIONS.md #2)"
    )


def _counterfactual_valid(being: int, meta: dict, run_manifest: dict) -> bool:
    """True only when this trace's `being` is VERIFIED to own `genome.bin`'s exact
    weights -- i.e. `weights.json` (from `genome.bin`) and `neural.trace` (from this
    being's recorded activity) describe the SAME individual, so a Counterfactual /
    `brain_step` recomputation over them is meaningful at all.

    Verified empirically (S2 follow-up, 2026-09-16, coordinator-routed): for
    `--resume --resume-mix 1`, population slot 0 is ALWAYS an exact, unmutated clone of
    the loaded checkpoint (`Universe/src/bin/gpu_evolve/main.rs`: `pop.push(best.clone())`
    runs before ANY `--resume-mix` scaling is applied to the OTHER slots). Confirmed by
    direct whole-file sha256 comparison against the source checkpoint for 4 real runs
    (`b3_fixed_s31_t8005`, `b3_legacy_s31_t8005`, `b3_fixed_s113_t8200`,
    `b3_legacy_nocost_s77_t8005`): every one of `evolve_best_gen0000.bin`'s hashes matched
    its `/media/llm-data/snapshots/b1-champions/*.bin` source exactly.

    Deliberately conservative: slot 0 is ALSO always the unmutated elite when
    `resume-mix < 1` (that code path is unconditional on the mix value), but this
    producer does not claim that case valid without the same kind of direct
    verification -- with `mix < 1` the OTHER slots are weaker, so slot 0 likely still
    wins the fitness ranking that decides what gets saved as `evolve_best_gen<gen>.bin`,
    but "likely" is not "verified". See `Universe/docs/LAB-UI-S2-GENOME-EXPORT.md` for
    the full writeup, including that `counterfactual_valid=True` says nothing about
    whether `brain_step` itself currently reproduces the recorded `raw_intent` (it does
    NOT, within the stage's quantisation, even for a verified-valid trace -- see the
    same doc's per-run error table. This field is about the GENOME being the right one,
    not about the reference forward being accurate yet).
    """
    args = run_manifest.get("args", {}) or {}
    if being != meta.get("selected_being"):
        return False  # explicit --being override: no relationship checked at all
    if not args.get("resume"):
        return False
    if being != 0:
        return False
    resume_mix = args.get("resume-mix")
    return resume_mix == 1 or resume_mix == 1.0


def _disabled_flags(run_manifest: dict) -> list[str]:
    command = run_manifest.get("command") or []
    present = [flag for flag in DISABLED_FLAG_NAMES if flag in command]
    return present


def _stage_genome_info(run_dir: Path, samples: list[dict], has_stages: bool) -> tuple[str | None, str | None]:
    """Returns `(genome_file, sha256)` for the schema-2 stage blocks about to be packed.

    Universe/docs/KERNELS-OBSERVATION-L1L2.md §11: "At each generation boundary the
    recorder also saves the selected slot as `observed_genome_genNNNN.bin`; every
    observation row names that file. Contributions can therefore be joined to the exact
    weights that produced them even after evolution changes the population." This reads
    exactly that name back out of the samples this trace actually packs, so `weights.json`
    (built by the caller from the returned filename) is verifiably the SAME individual
    that produced `l1_matmul`/`l1_to_l2`/etc., not merely "the generation's champion",
    which may differ (see `_being_selection_text`, DEVIATIONS.md #7).

    Returns `(None, None)` when `has_stages` is False (schema-1 run, or a schema-2 run
    whose selected samples do not all carry `stages`) -- the caller keeps schema-1
    behaviour: `weights.json` from the generation's own checkpoint, unchanged.

    Raises `ProducerError`, naming both values, when:
      - no sample names a `genome_file` at all (a schema-2 binary that regressed);
      - samples in this trace's range name MORE THAN ONE distinct `genome_file` --
        `weights.json` can only describe one genome, and the error names every
        candidate file together with its own sha256, so "these two genomes disagree"
        is never silently resolved by picking one;
      - the named file does not exist under `run_dir`.
    """
    if not has_stages:
        return None, None

    genome_files = sorted({s["genome_file"] for s in samples if isinstance(s.get("genome_file"), str)})
    if not genome_files:
        raise ProducerError(
            "observation_schema=2 and every selected sample carries 'stages', but none "
            "names a 'genome_file' -- cannot verify which weights produced these stage values"
        )
    if len(genome_files) > 1:
        per_file_sha256 = {
            name: (_sha256_file(run_dir / name) if (run_dir / name).exists() else "MISSING")
            for name in genome_files
        }
        raise ProducerError(
            f"samples in this trace's range name {len(genome_files)} different genome_file "
            f"values -- a trace-v1 directory's weights.json can only describe ONE genome, so "
            f"producing it would silently mix individuals: {per_file_sha256}"
        )

    genome_file = genome_files[0]
    genome_path = run_dir / genome_file
    if not genome_path.exists():
        raise ProducerError(
            f"observation.jsonl names genome_file={genome_file!r} for its recorded stages, "
            f"but {genome_path} does not exist"
        )
    return genome_file, _sha256_file(genome_path)


def _hashes(
    checkpoint_sha256: str, replay_sha256: str, config_sha256: str, neural_trace_sha256: str,
    observed_genome_file: str | None, observed_genome_sha256: str | None,
) -> dict:
    """manifest['hashes'] -- `observed_genome`/`observed_genome_file` are NEW, OPTIONAL
    keys (schema-2 only; see SCHEMA-CHANGE-observation_stage2_blocks.md and
    DEVIATIONS.md #13), absent entirely for a schema-1 trace so its `hashes` object
    stays byte-for-byte what it always was.
    """
    hashes = {
        "checkpoint": checkpoint_sha256,
        "replay": replay_sha256,
        "config": config_sha256,
        "neural_trace": neural_trace_sha256,
    }
    if observed_genome_sha256 is not None:
        hashes["observed_genome"] = observed_genome_sha256
        hashes["observed_genome_file"] = observed_genome_file
    return hashes


# The forward wall probe's cap is 50.0 m either way (Universe/src/bin/gpu_evolve/
# wall_probes.rs:91, the `distance(...)` call every caller -- continuous or legacy --
# passes 50.0 to), but what a recorded 50.0 MEANS depends on which probe kind produced
# it: on the continuous probe it is a real "wall is >=50 m away" reading; on the legacy
# stepped probe (src/bin/gpu_evolve/statics.rs continuous_wall_probes()==false) the probe
# itself only steps out to 30 m, so 50.0 there is a "nothing found within reach"
# sentinel, not a real distance between 30 and 50 m. `lab-ui/contract/REPLAY-FORMAT.md`
# documents `dist_wall_f` as "cap 30m", inherited from a stale comment in
# `Universe/src/replay.rs` -- the real cap recorded in the field is 50 m, only the
# LEGACY PROBE's reach is 30 m (see src/lab_api/DEVIATIONS.md #9).
_WALL_PROBE_MAX_M = 50.0
_WALL_PROBE_LEGACY_REACH_M = 30.0

_RECORDER_CONFIG_META_KEYS = (
    "slow_kinematics", "motor_head", "throttle_arbitration", "reverse_controller",
    "retina_geometry", "retina_encoding", "fov_degrees", "retina_rows", "retina_cols",
    "retina_pitch_radians", "sample_every", "road_view_calibration_version",
)


def _recorder_config(meta: dict) -> dict:
    """The recorder's own code-path configuration (driving.meta.json), copied into the
    manifest so a panel need not guess which of several historical code paths produced
    the numbers it is drawing -- see the coordinator note in DEVIATIONS.md #9 (S4 found
    that `dist_wall_f == 50.0` is ambiguous without knowing `wall_probes`).
    """
    config = {key: meta[key] for key in _RECORDER_CONFIG_META_KEYS if key in meta}
    wall_probe_kind = meta.get("wall_probes", "unknown")
    config["wall_probe_kind"] = wall_probe_kind
    config["wall_probe_max_m"] = _WALL_PROBE_MAX_M
    if wall_probe_kind == "legacy":
        config["wall_probe_reach_m"] = _WALL_PROBE_LEGACY_REACH_M
    return config


# ── events.json (contract/EVENTS.md) ────────────────────────────────────────────────

def _edge_events(frames: list[dict], key, kind: str, threshold: float, direction: str) -> list[dict]:
    """Shared edge-detection for brake_on/brake_off/near_wall (contract/EVENTS.md).

    `key` is a field name (str) or a callable(frame) -> float (used for near_wall's
    min-of-three-probes). `direction` is 'rising' (value crosses from <=threshold to
    >threshold, e.g. brake_on) or 'falling' (value crosses from >threshold to
    <=threshold, e.g. brake_off, near_wall). One call detects ONE direction/kind; a
    metric with both directions (brake) gets two separate calls.
    """
    events = []
    prev = None
    for frame in frames:
        value = frame[key] if not callable(key) else key(frame)
        if prev is not None:
            if direction == "rising" and prev <= threshold < value:
                events.append({"tick": frame["tick"], "kind": kind, "value": float(value)})
            elif direction == "falling" and prev > threshold >= value:
                events.append({"tick": frame["tick"], "kind": kind, "value": float(value)})
        prev = value
    return events


def _change_events(frames: list[dict], key: str, kind: str) -> list[dict]:
    events = []
    prev = None
    for frame in frames:
        value = frame[key]
        if prev is not None and value != prev:
            events.append({"tick": frame["tick"], "kind": kind, "value": float(value)})
        prev = value
    return events


def _impact_events_from_csv(run_dir: Path, gen: int, being: int) -> list[dict]:
    """contract/EVENTS.md 'impact': driving.csv windows for this (gen, being) with impact_ticks>0."""
    csv_path = run_dir / "driving.csv"
    if not csv_path.exists():
        return []
    events = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            if int(row["generation"]) != gen or int(row["being"]) != being:
                continue
            if int(row["impact_ticks"]) > 0:
                events.append({
                    "tick": int(row["last_tick"]),
                    "kind": "impact",
                    "value": float(row["impact_peak_mps"]),
                })
    return events


def _death_events(samples: list[dict]) -> list[dict]:
    events = []
    prev_alive = None
    for s in samples:
        alive = s.get("body", {}).get("alive")
        if alive is None:
            continue
        if prev_alive is True and alive is False:
            events.append({"tick": s["tick"], "kind": "death", "value": 1.0})
        prev_alive = alive
    return events


def build_events(run_dir: Path, gen: int, being: int, replay_path: Path, samples: list[dict]) -> list[dict]:
    _header, frames = rd.read_replay(replay_path, being=being)
    frames.sort(key=lambda fr: fr["tick"])

    events: list[dict] = []
    events += _edge_events(frames, key="final_brk", kind="brake_on", threshold=0.05, direction="rising")
    events += _edge_events(frames, key="final_brk", kind="brake_off", threshold=0.05, direction="falling")
    events += _change_events(frames, key="gear", kind="gear")
    events += _change_events(frames, key="laps", kind="lap")
    events += _edge_events(
        frames,
        key=lambda fr: min(fr["dist_wall_l"], fr["dist_wall_r"], fr["dist_wall_f"]),
        kind="near_wall",
        threshold=3.0,
        direction="falling",
    )
    events += _impact_events_from_csv(run_dir, gen, being)
    events += _death_events(samples)

    events.sort(key=lambda e: (e["tick"], e["kind"]))
    return events


# ── neural.trace block assembly ─────────────────────────────────────────────────────

class _BlockSpec:
    def __init__(self, name, dtype, unit, stage, extractor, shape_tail):
        self.name = name
        self.dtype = dtype  # numpy dtype string, e.g. '<f4'
        self.unit = unit
        self.stage = stage
        self.extractor = extractor  # sample -> python nested list/scalar matching shape_tail
        self.shape_tail = shape_tail

    def dtype_name(self) -> str:
        return {"<u4": "u32", "<i1": "i8", "<f4": "f32"}[self.dtype]


def _block_specs(meta: dict) -> list[_BlockSpec]:
    rows, cols = meta["retina_rows"], meta["retina_cols"]
    wave_channels = meta["wave_channels"]
    fast_values = meta["fast_state_values"]

    def motor(field):
        return lambda s: s["body"]["motor_trace"][field]

    return [
        # observation.jsonl stores 'retina' flat (rows*cols); reshape row-major into the
        # declared (rows, cols) shape (driving_diagnostics.rs writes it row-major, same
        # order retina.wgsl fills buf_retina_out).
        _BlockSpec("retina", "<u4", "u32 packed: low byte material id, distance_mm upper 24 bits", None,
                   lambda s: [s["retina"][r * cols:(r + 1) * cols] for r in range(rows)], (rows, cols)),
        _BlockSpec("wave", "<i1", "dimensionless i8 channel value", None,
                   lambda s: s["wave"], (wave_channels,)),
        _BlockSpec("cfc", "<f4", "dimensionless", "sensory_cfc_pre_l1",
                   lambda s: s["fast_state"], (fast_values,)),
        _BlockSpec("raw_intent", "<f4", "throttle,steer,brake", "raw_intent", motor("raw_intent"), (3,)),
        _BlockSpec("after_head", "<f4", "throttle,steer,brake", "after_head", motor("after_head"), (3,)),
        _BlockSpec("after_modulation", "<f4", "throttle,steer,brake", "after_modulation", motor("after_modulation"), (3,)),
        _BlockSpec("final_command", "<f4", "throttle,steer,brake", "final_command", motor("final_command"), (3,)),
        _BlockSpec("pose", "<f4", "x_m,z_m,forward_x,forward_z", None,
                   lambda s: [s["body"]["x"], s["body"]["z"], s["body"]["forward"][0], s["body"]["forward"][1]],
                   (4,)),
        _BlockSpec(
            "body", "<f4",
            "speed_mps,alive,life,fuel,gear,damage,rpm,rpm_fraction,slip_ratio_peak,slip_angle_peak_rad,contact_mask,impact_mps",
            None,
            lambda s: [
                s["body"]["speed"], float(bool(s["body"]["alive"])), s["body"]["life"], s["body"]["fuel"],
                s["body"]["gear"], s["body"]["damage"], s["body"]["rpm"], s["body"]["rpm_fraction"],
                s["body"]["slip_ratio_peak"], s["body"]["slip_angle_peak_rad"],
                s["body"]["contact_mask"], s["body"]["impact_mps"],
            ],
            (12,),
        ),
    ]


def _sample_has_motor_trace(sample: dict) -> bool:
    return isinstance(sample.get("body", {}).get("motor_trace"), dict)


def _sample_has_stages(sample: dict) -> bool:
    return isinstance(sample.get("stages"), dict)


def _stage2_block_specs() -> list[_BlockSpec]:
    """The nine schema-2 stage blocks (Universe/docs/KERNELS-OBSERVATION-L1L2.md §3),
    inserted into `_all_block_specs` right after `cfc` (the recurrent state they read)
    and before `raw_intent` (the motor chain `final_intent[0:3]` feeds) -- the same
    execution-order slot the doc's `brain_graph` gives them.
    """
    def stage(name):
        return lambda s: s["stages"][name]

    return [
        _BlockSpec("l1_matmul", "<f4", "dimensionless", "l1_matmul", stage("l1_matmul"), (96,)),
        _BlockSpec("l1_effective", "<f4", "dimensionless", "l1_effective", stage("l1_effective"), (96,)),
        _BlockSpec("l1_to_l2", "<i1", "sensor_code", "l1_to_l2", stage("l1_to_l2"), (96,)),
        _BlockSpec("l2_matmul", "<f4", "dimensionless", "l2_matmul", stage("l2_matmul"), (48,)),
        _BlockSpec("l2_effective", "<f4", "dimensionless", "l2_effective", stage("l2_effective"), (48,)),
        _BlockSpec("l2_std", "<f4", "dimensionless", "l2_std", stage("l2_std"), ()),
        _BlockSpec("l2_adapted", "<f4", "dimensionless", "l2_adapted", stage("l2_adapted"), (48,)),
        _BlockSpec("bypass_adapted", "<f4", "dimensionless", "bypass_adapted", stage("bypass_adapted"), (48,)),
        _BlockSpec("final_intent", "<f4", "dimensionless", "final_intent", stage("final_intent"), (96,)),
    ]


def _all_block_specs(meta: dict, schema2: bool) -> list[_BlockSpec]:
    """`_block_specs` (schema-1, unchanged) plus the nine schema-2 stage specs spliced
    in right after `cfc`, only when `schema2` is True. Keeping schema-1's own list and
    order byte-for-byte unchanged is the point -- see `producer.py`'s module doc and
    `SCHEMA-CHANGE-observation_stage2_blocks.md`.
    """
    specs = _block_specs(meta)
    if not schema2:
        return specs
    idx = next(i for i, s in enumerate(specs) if s.name == "cfc") + 1
    return specs[:idx] + _stage2_block_specs() + specs[idx:]


def build_neural_trace(
    samples: list[dict], meta: dict, profile: str, schema2: bool, has_stages: bool,
) -> tuple[bytes, list[dict], list[dict]]:
    """Returns (neural_trace_bytes, block_table[], absent[]).

    `absent` entries here are ONLY for neural.trace blocks (the coarse l1/l2/intent
    schema-1 placeholders, OR the nine schema-2 stage blocks when `has_stages` is
    False; plus the four motor_trace-derived blocks when no sample in range carries
    motor_trace; plus every block when profile='summary'). weights.json/track.json
    absences are added by the caller, not here.

    `schema2`/`has_stages` are computed ONCE by the caller (`produce`), which also
    needs them to decide `weights.json`'s genome source and `brain_schema_version` --
    passed in rather than recomputed here so the two never drift apart.
    """
    if schema2:
        absent: list[dict] = []
    else:
        absent = [{"name": name, "reason": reason} for name, reason in _NEVER_RECORDED_STAGES]

    if profile == "summary":
        for spec in _all_block_specs(meta, schema2):
            absent.append({"name": spec.name, "reason": "profile 'summary' carries no neural blocks by design"})
        return b"", [], absent

    has_motor_trace = all(_sample_has_motor_trace(s) for s in samples) if samples else False

    blocks_out: list[dict] = []
    payload = bytearray()
    offset = 0
    for spec in _all_block_specs(meta, schema2):
        if spec.name in _MOTOR_BLOCK_NAMES and not has_motor_trace:
            absent.append({"name": spec.name, "reason": "body.motor_trace missing on at least one sample in range"})
            continue
        if spec.name in _STAGE2_BLOCK_NAMES and not has_stages:
            absent.append({
                "name": spec.name,
                "reason": "stages missing on at least one sample in range (brain_skip tick, or observation_schema != 2)",
            })
            continue
        rows = [spec.extractor(s) for s in samples]
        arr = np.asarray(rows, dtype=spec.dtype)
        expected_shape = (len(samples),) + spec.shape_tail
        if arr.shape != expected_shape:
            raise ProducerError(
                f"block {spec.name!r}: built array has shape {arr.shape}, expected {expected_shape}"
            )
        raw = arr.tobytes(order="C")
        block_sha = _sha256_bytes(raw)
        blocks_out.append({
            "name": spec.name,
            "dtype": spec.dtype_name(),
            "shape": list(arr.shape),
            "unit": spec.unit,
            "scale": 1.0,
            "offset": offset,
            "length": len(raw),
            "compression": "none",
            "stage": spec.stage,
            "sha256": block_sha,
        })
        payload += raw
        offset += len(raw)

    return bytes(payload), blocks_out, absent


# ── main entry point ────────────────────────────────────────────────────────────────

def produce(run_dir: str | Path, gen: int, being: int | None = None, profile: str = "champion",
            force: bool = False) -> Path:
    run_dir = Path(run_dir)
    run_name = run_dir.name

    if profile not in ("summary", "champion", "event", "full"):
        raise ProducerError(f"unknown profile {profile!r}; expected summary|champion|event|full")

    meta_path = run_dir / "driving.meta.json"
    if not meta_path.exists():
        raise ProducerError(f"{meta_path} does not exist -- was --driving-diagnostics used for this run?")
    meta = _read_json(meta_path)

    run_manifest_path = run_dir / "manifest.json"
    if not run_manifest_path.exists():
        raise ProducerError(f"{run_manifest_path} does not exist -- not a run directory")
    run_manifest = _read_json(run_manifest_path)

    if being is None:
        being = int(meta.get("selected_being", 0))

    # PRD S5, "Validation is mandatory at three points": (1) the producer validates
    # EVERY sample against driving.meta.json FIRST, before any other read.
    trace_check.check_run(run_dir)

    genome_path = _find_genome_path(run_dir, gen)
    replay_path = _find_replay_path(run_dir, gen)

    checkpoint_sha256 = _sha256_file(genome_path)
    replay_sha256 = _sha256_file(replay_path)
    config_sha256 = _sha256_file(run_manifest_path)

    trace_dir = run_dir / "trace" / f"gen{gen:04d}" / f"being{being:02d}" / profile
    existing_manifest_path = trace_dir / "manifest.json"
    if existing_manifest_path.exists() and not force:
        try:
            existing = _read_json(existing_manifest_path)
            existing_hashes = existing.get("hashes", {})
            if (
                existing_hashes.get("checkpoint") == checkpoint_sha256
                and existing_hashes.get("replay") == replay_sha256
                and existing_hashes.get("config") == config_sha256
            ):
                raise TraceUpToDate(trace_dir)
        except (json.JSONDecodeError, OSError):
            pass  # a corrupt/partial existing manifest is treated as "needs rebuilding"

    all_samples = list(_iter_generation_samples(run_dir, gen, being))
    if not all_samples:
        raise ProducerError(f"no observation.jsonl samples for generation={gen} being={being} in {run_dir}")
    all_samples.sort(key=lambda s: s["tick"])

    events = build_events(run_dir, gen, being, replay_path, all_samples)

    if profile == "event":
        window = 64
        event_ticks = [e["tick"] for e in events]
        kept = [
            s for s in all_samples
            if any(abs(s["tick"] - t) <= window for t in event_ticks)
        ]
        samples = kept if kept else all_samples[:0]
    else:
        # 'summary', 'champion', 'full' -- 'full' is an alias of 'champion' today (the
        # producer has no denser source than observation.jsonl's own sample_every
        # cadence; PRD S3's 'full' = every tick is not attainable from this recorder).
        samples = all_samples

    if not samples:
        raise ProducerError(
            f"profile={profile!r} selected zero samples for generation={gen} being={being} "
            f"(no events found to window around)"
        )

    # Universe/docs/KERNELS-OBSERVATION-L1L2.md §5: `driving.meta.json.observation_schema`
    # is bumped to 2 when the recorder's binary packs the exact L1/L2 stage arrays into
    # every observation.jsonl row's `stages` object. `has_stages` additionally requires
    # every SELECTED sample (post profile filtering) to actually carry one -- a schema-2
    # binary still writes `stages: null` on a `brain_skip` tick (§11).
    schema2 = meta.get("observation_schema") == 2
    has_stages = schema2 and all(_sample_has_stages(s) for s in samples)

    # doc §11: "every observation row names that file [the exact genome that produced
    # it]" -- SCHEMA-CHANGE-observation_stage2_blocks.md's reasoning for why weights.json
    # must be exported from THIS file, not unconditionally from the generation's
    # checkpoint, once real stage blocks are being packed (the recorded being need not be
    # the fitness champion -- see `_being_selection_text`/DEVIATIONS.md #7).
    observed_genome_file, observed_genome_sha256 = _stage_genome_info(run_dir, samples, has_stages)

    neural_bytes, blocks, trace_absent = build_neural_trace(samples, meta, profile, schema2, has_stages)

    trace_dir.mkdir(parents=True, exist_ok=True)
    neural_trace_path = trace_dir / "neural.trace"
    neural_trace_path.write_bytes(neural_bytes)
    neural_trace_sha256 = _sha256_file(neural_trace_path)

    # weights.json via the Rust exporter -- never reparsed/reimplemented here. Schema-1
    # behaviour (no observed_genome_file) is UNCHANGED: always the generation's own
    # checkpoint (evolve_best_gen<NNNN>.bin).
    weights_source_path = genome_path if observed_genome_file is None else (run_dir / observed_genome_file)
    weights_path = trace_dir / "weights.json"
    _run_binary([_binary_path("genome_export"), str(weights_source_path), str(weights_path)], "genome_export")

    # track.json via the Rust track exporter -- same VoxelWorld constructor the sim uses.
    absent = list(trace_absent)
    args = run_manifest.get("args", {}) or {}
    tracks = args.get("tracks") or []
    width = args.get("width")
    track_path = trace_dir / "track.json"
    if tracks and width is not None:
        if len(tracks) > 1:
            # Track rotation: this producer exports the FIRST configured seed only --
            # see src/lab_api/DEVIATIONS.md. Good enough for today's fixed-track runs
            # (b1/b3/b5); a rotating run needs a real per-generation seed lookup.
            pass
        seed = tracks[0]
        _run_binary([_binary_path("track_export"), str(seed), str(width), str(track_path)], "track_export")
    else:
        absent.append({"name": "track.json", "reason": "run manifest has no args.tracks/args.width to build it from"})

    events_path = trace_dir / "events.json"
    with open(events_path, "w") as f:
        json.dump(events, f, indent=1)

    replay_link = trace_dir / "physical.replay"
    genome_link = trace_dir / "genome.bin"
    for link, target in ((replay_link, replay_path), (genome_link, genome_path)):
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(target.resolve())

    samples_tick = [s["tick"] for s in samples]
    manifest = {
        "magic": "trace-v1",
        "schema_version": SCHEMA_VERSION,
        "endian": "little",
        "run": run_name,
        "generation": gen,
        "being": being,
        "being_selection": _being_selection_text(being, gen, meta, run_manifest),
        "profile": profile,
        "first_tick": samples_tick[0],
        "count": len(samples_tick),
        "stride": int(meta.get("sample_every", 1)),
        "samples_tick": samples_tick,
        "blocks": blocks,
        "body_schema_version": BODY_SCHEMA_VERSION,
        # Bumped to 2 only when the nine schema-2 stage blocks were actually packed
        # (`has_stages`) -- a schema-2 RUN whose selected samples happen to lack
        # `stages` (see build_neural_trace's absent reason) still stays at 1, because
        # this trace-v1 directory itself carries no schema-2 brain-stage blocks.
        "brain_schema_version": 2 if has_stages else BRAIN_SCHEMA_VERSION,
        "hashes": _hashes(checkpoint_sha256, replay_sha256, config_sha256, neural_trace_sha256,
                           observed_genome_file, observed_genome_sha256),
        "universe_commit": run_manifest.get("universe_commit", "unknown"),
        "world_seed": rd.read_replay_header(replay_path)["world_seed"],
        "absent": absent,
        "disabled_flags": _disabled_flags(run_manifest),
        # S4 finding (see DEVIATIONS.md #9): a panel cannot tell a real 50 m continuous
        # wall reading from a legacy probe's "nothing within reach" sentinel without
        # knowing which code path recorded it. `recorder_config` is a NEW, OPTIONAL
        # top-level object -- the schema has `additionalProperties: false`, so this is
        # a genuine schema change; see SCHEMA-CHANGE-recorder_config.md and
        # DEVIATIONS.md #9 for why only the vendored copy could be updated here.
        "recorder_config": _recorder_config(meta),
        # Coordinator follow-up (2026-09-16): whether `being` is VERIFIED to own
        # genome.bin's exact weights -- see _counterfactual_valid's docstring and
        # SCHEMA-CHANGE-counterfactual_valid.md. Independent of whether brain_step
        # itself currently matches (it does not yet -- Universe/docs/LAB-UI-S2-GENOME-EXPORT.md).
        "counterfactual_valid": _counterfactual_valid(being, meta, run_manifest),
    }
    # NOTE: 'full' is produced identically to 'champion' by this producer today (PRD S2
    # task text says so explicitly) -- NOT recorded as an extra manifest key, because
    # the schema's additionalProperties:false forbids one; see TESTING.md instead.

    manifest_path = trace_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=1)

    # Validate our own output before declaring success (PRD S5 validation point applies
    # to every consumer, including the producer that just wrote the bytes).
    trace_check.check_trace_dir(trace_dir)

    return trace_dir


def register(trace_dir: Path, db_path: str = lab_db.DEFAULT_PATH) -> None:
    """Registers a produced trace in lab.db (PRD S2 item 6). Requires the run to already
    be ingested (trace.run_name has a foreign key to run.name) -- ingests it first,
    idempotently.
    """
    manifest = _read_json(trace_dir / "manifest.json")
    run_dir = trace_dir.parent.parent.parent.parent  # trace/genNNNN/beingNN/profile -> run_dir
    db = lab_db.connect(db_path)
    lab_db.ingest_run(db, str(run_dir))
    size_bytes = sum(f.stat().st_size for f in trace_dir.iterdir() if f.is_file())
    manifest_sha256 = _sha256_file(trace_dir / "manifest.json")
    lab_db.register_trace(
        db,
        run=manifest["run"],
        gen=manifest["generation"],
        being=manifest["being"],
        profile=manifest["profile"],
        path=str(trace_dir),
        schema_version=manifest["schema_version"],
        manifest_sha256=manifest_sha256,
        size_bytes=size_bytes,
    )
