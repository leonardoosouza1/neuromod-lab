"""Tests for the S2 trace-v1 producer (`lab_api.trace.producer`/`produce`).

Runs against REAL finished Universe runs, copied into scratch first (never mutates the
live run directories under `/media/llm-data/universe-runs/`, even though the "Where"
rule for this task explicitly allows writing into a finished run's own `trace/`
subtree -- copying keeps this test hermetic and repeatable regardless of what else is
touching the live runs root).

    /home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_trace_producer.py -v

See TESTING.md for the exact command from a clean checkout, with pasted output.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lab_api.trace import check as check_module  # noqa: E402
from lab_api.trace import producer as trace_producer  # noqa: E402
from lab_api.trace import reference_decoder as rd  # noqa: E402

RUNS_ROOT = Path("/media/llm-data/universe-runs/neuromod-lab-taxi")
SCRATCH_ROOT = Path("/media/llm-data/scratch/s2-pack/test_producer")
REPO_ROOT = Path(__file__).resolve().parents[1]
from conftest import find_lab_ui  # noqa: E402  (tests/ is on sys.path under pytest)

LAB_UI_REPO = find_lab_ui()
B2_FIXTURE_DIR = LAB_UI_REPO / "fixtures" / "trace-v1" / "universe-b2-gen0"
CONTRACT_DIR = LAB_UI_REPO / "contract"

# The S0 fixture's own SOURCE.md: cut from this run, generation 0, being 0.
B2_SOURCE_RUN = "b2_cost_s113"

B3_SPARSE_RUN = "b3_fixed_s31_t8005"  # gens=1, --resume, sample_every=2000 (10 samples)
B5_DENSE_RUN = "b5_ctrl_s31"  # gens=25, no --resume, sample_every=16 (750 samples/gen)
B5_DENSE_GEN = 24  # last generation


def _require_universe_bin(name: str) -> None:
    path = Path(trace_producer.DEFAULT_UNIVERSE_BIN_DIR) / name
    if not path.exists():
        pytest.skip(f"{path} not built -- see TESTING.md's Rust build step")


def _require_node() -> None:
    if shutil.which("node") is None:
        pytest.skip("node not found on PATH -- JS decoder cross-check needs it")


def _copy_run_minimal(src: Path, dst: Path, generations: list[int]) -> Path:
    """Copies a run directory into scratch, keeping only the files `produce()` needs
    for the listed generations, plus every top-level manifest/meta/observation/csv file
    (small; observation.jsonl is the only sizeable one, and is needed in full for
    `check_run`'s own validation and for the generation filter).
    """
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("manifest.json", "driving.meta.json", "observation.jsonl", "driving.csv"):
        src_file = src / name
        if src_file.exists():
            shutil.copy2(src_file, dst / name)
    for gen in generations:
        for pattern in (f"evolve_best_gen{gen:04d}.bin", f"gen{gen:04d}.replay",
                        f"gen{gen:04d}.meta.json", f"population_gen{gen:04d}.json",
                        f"laps_gen{gen:04d}.jsonl"):
            src_file = src / pattern
            if src_file.exists():
                shutil.copy2(src_file, dst / pattern)
    return dst


@pytest.fixture(scope="module")
def b3_scratch_copy():
    src = RUNS_ROOT / B3_SPARSE_RUN
    if not src.exists():
        pytest.skip(f"{src} not present on this machine")
    dst = SCRATCH_ROOT / B3_SPARSE_RUN
    if dst.exists():
        shutil.rmtree(dst)
    return _copy_run_minimal(src, dst, generations=[0])


@pytest.fixture(scope="module")
def b5_scratch_copy():
    src = RUNS_ROOT / B5_DENSE_RUN
    if not src.exists():
        pytest.skip(f"{src} not present on this machine")
    dst = SCRATCH_ROOT / B5_DENSE_RUN
    if dst.exists():
        shutil.rmtree(dst)
    return _copy_run_minimal(src, dst, generations=[B5_DENSE_GEN])


# ── structure (sparse run, --resume) ────────────────────────────────────────────────

def test_produce_sparse_resumed_run_validates_and_decodes(b3_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")

    trace_dir = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion")
    assert trace_dir == b3_scratch_copy / "trace" / "gen0000" / "being00" / "champion"

    manifest = check_module.check_trace_dir(trace_dir)  # raises on any mismatch
    assert manifest["count"] == 10  # sample_every=2000, ticks=20000
    assert manifest["run"] == B3_SPARSE_RUN
    assert "resume" in manifest["being_selection"], manifest["being_selection"]
    assert manifest["recorder_config"]["wall_probe_kind"] in ("continuous", "legacy")
    assert manifest["recorder_config"]["wall_probe_max_m"] == 50.0

    for name in ("physical.replay", "genome.bin"):
        link = trace_dir / name
        assert link.is_symlink()
        assert link.resolve().exists()

    for block in manifest["blocks"]:
        arr = rd.read_block(trace_dir, block["name"], manifest=manifest)
        assert list(arr.shape) == block["shape"]

    events = json.loads((trace_dir / "events.json").read_text())
    assert isinstance(events, list)
    ticks = [e["tick"] for e in events]
    assert ticks == sorted(ticks)

    weights = json.loads((trace_dir / "weights.json").read_text())
    assert weights["genome_sha256"] == manifest["hashes"]["checkpoint"]
    assert "l1" in weights["brain_flow"]

    track = json.loads((trace_dir / "track.json").read_text())
    assert track["seed"] == manifest["world_seed"]
    assert len(track["waypoints"]) > 0

    assert manifest["counterfactual_valid"] is True, (
        "b3_fixed_s31_t8005 is --resume --resume-mix 1, being 0 -- must be marked verified"
    )


B1_CHAMPIONS_DIR = Path("/media/llm-data/snapshots/b1-champions")


def test_resume_mix_one_slot_zero_is_byte_identical_to_the_loaded_champion(b3_scratch_copy):
    """Regression guard for the coordinator's genome-ownership check (2026-09-16):
    population slot 0 under --resume is ALWAYS `best.clone()` with no --resume-mix
    scaling applied (Universe/src/bin/gpu_evolve/main.rs, `pop.push(best.clone())` runs
    before the mix loop touches any OTHER slot), so `evolve_best_gen0000.bin` saved at
    the end of a --resume --resume-mix 1 run must be byte-identical to the checkpoint
    that was loaded. b3_fixed_s31_t8005 loaded b1_fixed_s31.bin
    (neuromod-lab/scripts/enqueue_b3_b2.py's B3 recipe: the champion is copied to
    <out>/evolve_best_gen0000.bin before --resume runs).
    """
    champion_source = B1_CHAMPIONS_DIR / "b1_fixed_s31.bin"
    if not champion_source.exists():
        pytest.skip(f"{champion_source} not present on this machine")

    saved = b3_scratch_copy / "evolve_best_gen0000.bin"
    assert saved.exists()

    import hashlib

    def sha256_file(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    assert sha256_file(saved) == sha256_file(champion_source), (
        "evolve_best_gen0000.bin must be byte-identical to the loaded champion for a "
        "--resume --resume-mix 1 run -- if this fails, either the run's own recipe "
        "changed or the counterfactual_valid=True guarantee no longer holds"
    )


def test_counterfactual_valid_false_when_run_did_not_resume(b5_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    # force=True: another test in this module-scoped-fixture file may already have
    # produced this exact (gen, being, profile) -- this test wants the artifact, not to
    # re-test idempotency (covered elsewhere).
    trace_dir = trace_producer.produce(b5_scratch_copy, gen=B5_DENSE_GEN, profile="champion", force=True)
    manifest = json.loads((trace_dir / "manifest.json").read_text())
    assert manifest["counterfactual_valid"] is False


def test_check_cli_exits_zero_on_produced_trace(b3_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    trace_dir = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=True)
    result = subprocess.run(
        [sys.executable, "-m", "lab_api.trace.check", str(trace_dir)],
        cwd=str(REPO_ROOT / "src"),
        env={**os.environ, "PYTHONPATH": "."},
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_js_decoder_agrees_with_python_decoder(b3_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    _require_node()
    trace_dir = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=True)

    # The JS decoder validates against a schema file living next to decoder.js/replay.js
    # in lab-ui/contract -- but S2 added an OPTIONAL 'recorder_config' object only to the
    # VENDORED schema copy (src/lab_api/DEVIATIONS.md #9/#10: this worktree has no
    # lab-ui checkout to edit the canonical one). Build a scratch "contract dir" that
    # symlinks the real decoder.js/replay.js but the VENDORED (ahead) schema, so this
    # cross-check exercises the same schema the Python side just validated against.
    if not CONTRACT_DIR.exists():
        pytest.fail(f"{CONTRACT_DIR} not present -- set LAB_UI_REPO; a contract check that skips hides drift")
    vendored_contract = SCRATCH_ROOT / "contract-vendored"
    vendored_contract.mkdir(parents=True, exist_ok=True)
    for name in ("decoder.js", "replay.js", "package.json"):
        link = vendored_contract / name
        if not link.exists():
            link.symlink_to(CONTRACT_DIR / name)
    vendored_schema_link = vendored_contract / "trace-v1.schema.json"
    if vendored_schema_link.is_symlink() or vendored_schema_link.exists():
        vendored_schema_link.unlink()
    vendored_schema_link.symlink_to(REPO_ROOT / "src" / "lab_api" / "trace" / "trace-v1.schema.json")

    result = subprocess.run(
        ["node", str(REPO_ROOT / "tests" / "decode_fixture.mjs"), str(trace_dir), str(vendored_contract)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    js_summary = json.loads(result.stdout)

    manifest = rd.load_manifest(trace_dir)
    assert js_summary["manifest_run"] == manifest["run"]
    assert js_summary["manifest_count"] == manifest["count"]
    for block in manifest["blocks"]:
        py_arr = rd.read_block(trace_dir, block["name"], manifest=manifest)
        js_block = js_summary["blocks"][block["name"]]
        assert js_block["length"] == py_arr.size, block["name"]
        # First/last 8 values, allowing f32 round-trip noise through JSON's f64.
        py_first8 = py_arr.reshape(-1)[:8].astype("float64").tolist()
        py_last8 = py_arr.reshape(-1)[-8:].astype("float64").tolist()
        for a, b in zip(py_first8, js_block["first8"]):
            assert a == pytest.approx(b, abs=1e-3), block["name"]
        for a, b in zip(py_last8, js_block["last8"]):
            assert a == pytest.approx(b, abs=1e-3), block["name"]


# ── idempotency ──────────────────────────────────────────────────────────────────────

def test_idempotent_refuses_then_force_rebuilds_byte_identically(b3_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")

    trace_dir = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=True)
    neural_before = (trace_dir / "neural.trace").read_bytes()
    manifest_before = json.loads((trace_dir / "manifest.json").read_text())

    with pytest.raises(trace_producer.TraceUpToDate) as exc_info:
        trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=False)
    assert exc_info.value.trace_dir == trace_dir

    trace_dir_again = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=True)
    assert trace_dir_again == trace_dir
    neural_after = (trace_dir / "neural.trace").read_bytes()
    manifest_after = json.loads((trace_dir / "manifest.json").read_text())

    assert neural_before == neural_after, "forced rebuild must be byte-identical for unchanged sources"
    assert manifest_before["hashes"] == manifest_after["hashes"]
    assert manifest_before["samples_tick"] == manifest_after["samples_tick"]


# ── density (real finished run with many samples) ───────────────────────────────────

def test_produce_dense_unresumed_run_champion_profile(b5_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")

    # force=True: test_counterfactual_valid_false_when_run_did_not_resume (above) may
    # already have produced this exact (gen, being, profile) via the same module-scoped
    # fixture; idempotency itself is covered by
    # test_idempotent_refuses_then_force_rebuilds_byte_identically.
    trace_dir = trace_producer.produce(b5_scratch_copy, gen=B5_DENSE_GEN, profile="champion", force=True)
    manifest = check_module.check_trace_dir(trace_dir)
    assert manifest["count"] == 750  # 12000 ticks / sample_every=16
    assert "NOT verified to be the fitness champion" in manifest["being_selection"]

    body_block = next(b for b in manifest["blocks"] if b["name"] == "body")
    assert body_block["shape"] == [750, 12]

    events = json.loads((trace_dir / "events.json").read_text())
    assert len(events) > 0


def test_summary_profile_has_zero_blocks_and_still_validates(b5_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")

    trace_dir = trace_producer.produce(b5_scratch_copy, gen=B5_DENSE_GEN, profile="summary", force=True)
    manifest = check_module.check_trace_dir(trace_dir)
    assert manifest["blocks"] == []
    absent_names = {a["name"] for a in manifest["absent"]}
    for name in ("retina", "wave", "cfc", "raw_intent", "after_head", "after_modulation", "final_command", "pose", "body"):
        assert name in absent_names, f"{name} must be listed absent for profile=summary"
    assert (trace_dir / "neural.trace").stat().st_size == 0


def test_event_profile_windows_around_events(b5_scratch_copy):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")

    # force=True: a prior test in this module may have already produced the champion
    # trace for this same scratch copy (module-scoped fixture) -- this test wants the
    # artifact, idempotency itself is covered by test_idempotent_refuses_then_force_rebuilds_byte_identically.
    champion_dir = trace_producer.produce(b5_scratch_copy, gen=B5_DENSE_GEN, profile="champion", force=True)
    champion_manifest = json.loads((champion_dir / "manifest.json").read_text())

    event_dir = trace_producer.produce(b5_scratch_copy, gen=B5_DENSE_GEN, profile="event", force=True)
    event_manifest = check_module.check_trace_dir(event_dir)

    assert event_manifest["count"] <= champion_manifest["count"]
    events = json.loads((event_dir / "events.json").read_text())
    if events:
        event_ticks = [e["tick"] for e in events]
        for tick in event_manifest["samples_tick"]:
            assert any(abs(tick - t) <= 64 for t in event_ticks), (
                f"tick {tick} in the 'event' profile trace is not within 64 ticks of any event"
            )


# ── DB registration ──────────────────────────────────────────────────────────────────

def test_register_writes_trace_row_into_a_scratch_db(b3_scratch_copy, tmp_path):
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    sys.path.insert(0, str(REPO_ROOT / "src"))
    import lab_db  # noqa: E402  (top-level module, see conftest.py's sys.path shim)

    trace_dir = trace_producer.produce(b3_scratch_copy, gen=0, profile="champion", force=True)
    db_path = str(tmp_path / "lab_test.db")
    trace_producer.register(trace_dir, db_path=db_path)

    db = lab_db.connect(db_path)
    rows = lab_db.traces(db, run=B3_SPARSE_RUN)
    assert len(rows) == 1
    assert rows[0]["gen"] == 0
    assert rows[0]["being"] == 0
    assert rows[0]["profile"] == "champion"
    assert rows[0]["path"] == str(trace_dir)

    runs = lab_db.runs(db)
    assert any(r["name"] == B3_SPARSE_RUN for r in runs), "register() must ingest the run (trace.run_name FK)"


# ── agreement with the S0 hand-cut fixture, same source ─────────────────────────────

def test_producer_output_agrees_with_s0_fixture_on_shared_blocks():
    """lab-ui/fixtures/trace-v1/universe-b2-gen0/SOURCE.md: cut by hand from
    b2_cost_s113, generation 0, being 0, first 300 observation.jsonl samples. If that
    source run is still on disk, reproduce it with the producer and compare every block
    both carry over the SAME tick range -- the fixture's own values must reappear
    exactly (same source bytes, S0 verified this by hand; a real disagreement here would
    mean the producer decodes a field differently than S0 did).
    """
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    if not B2_FIXTURE_DIR.exists():
        pytest.fail(f"{B2_FIXTURE_DIR} not present -- set LAB_UI_REPO")
    src = RUNS_ROOT / B2_SOURCE_RUN
    if not src.exists():
        pytest.skip(f"{src} (the fixture's source run) is gone from this machine -- cannot cross-check")

    dst = SCRATCH_ROOT / B2_SOURCE_RUN
    if dst.exists():
        shutil.rmtree(dst)
    _copy_run_minimal(src, dst, generations=[0])

    trace_dir = trace_producer.produce(dst, gen=0, being=0, profile="champion")
    manifest = rd.load_manifest(trace_dir)
    fixture_manifest = rd.load_manifest(B2_FIXTURE_DIR)

    n = fixture_manifest["count"]  # fixture kept only the first 300 samples
    for block in fixture_manifest["blocks"]:
        fixture_arr = rd.read_block(B2_FIXTURE_DIR, block["name"], manifest=fixture_manifest)
        produced_arr = rd.read_block(trace_dir, block["name"], manifest=manifest)[:n]
        assert produced_arr.shape == fixture_arr.shape, block["name"]
        import numpy as np
        assert np.array_equal(produced_arr, fixture_arr), (
            f"block {block['name']!r} disagrees with the S0 fixture on the same source range"
        )


# ── dense, genome-verified integration fixture (coordinator, 2026-09-16) ────────────

DENSE_FIXTURE_RUN = "champ_nocost_s77_dense_t8005"


def test_dense_integration_fixture_is_a_healthy_driving_trace_not_a_parked_one():
    """champ_nocost_s77_dense_t8005: champion of b1_nocost_s77 (8-lap, zero-collision),
    --resume --resume-mix 1, --vision-every 4 on 12000 ticks -> 3000 samples. Produced
    directly against the LIVE run dir (read-only checks + the trace/ subtree the PRD
    allows for a FINISHED run -- this run is finished, gens=1/gens_complete=1). Intended
    as the micro view's integration fixture going forward: the S0 fixture is a
    generation-0 being parked against a wall (~90% of retina pixels are wall at ~6.5 m),
    which exercises decoding but not driving; this one actually drives.
    """
    _require_universe_bin("genome_export")
    _require_universe_bin("track_export")
    run_dir = RUNS_ROOT / DENSE_FIXTURE_RUN
    if not run_dir.exists():
        pytest.skip(f"{run_dir} not present on this machine")
    if not (run_dir / "population_gen0000.json").exists():
        pytest.skip(f"{run_dir} has not finished yet (no population_gen0000.json)")

    try:
        trace_dir = trace_producer.produce(run_dir, gen=0, profile="champion")
    except trace_producer.TraceUpToDate as exc:
        # A prior run of this test (or the manual smoke in TESTING.md) already produced
        # it against this same, unchanging FINISHED run -- idempotency working as
        # designed, not a failure.
        trace_dir = exc.trace_dir
    manifest = check_module.check_trace_dir(trace_dir)
    assert manifest["count"] == 3000
    assert manifest["counterfactual_valid"] is True

    body = rd.read_block(trace_dir, "body", manifest=manifest)
    speed = body[:, 0]
    alive = body[:, 1]
    assert speed.mean() > 5.0, "expected a genuinely driving being, not one parked at low speed"
    assert alive.mean() == 1.0, "expected the being to survive the whole recorded window"

    retina = rd.read_block(trace_dir, "retina", manifest=manifest)
    wall_material_fraction = ((retina & 0xFF) == 2).mean()
    assert wall_material_fraction < 0.85, (
        "retina is mostly wall-material -- this would be a parked/stuck fixture, not a driving one"
    )

    events = json.loads((trace_dir / "events.json").read_text())
    assert any(e["kind"] == "lap" for e in events), "expected at least one completed lap"
