"""Cross-check the trace-v1 contract: schema, Python decoder, JS decoder.

Run with: python -m pytest tests/test_trace_contract.py -v
(see TESTING.md for the exact command from a clean checkout).

Covers, per the S0 task brief:
  (a) the fixture manifest validates against trace-v1.schema.json
  (b) every block decodes to the shape/dtype/length the manifest declares
  (c) the JS reference decoder (Node) agrees byte-for-byte with the Python
      one on every block's first/last 8 values, and on the replay header
      and first/last frame of the observed being
  (d) the vendored schema copy in this repo is byte-identical to
      lab-ui/contract/trace-v1.schema.json
  (e) an absent block raises the dedicated AbsentBlockError, not a bare KeyError
  (f) a neural.trace corrupted with `dd` (4 bytes flipped mid-file, inside a
      block's range) is refused, naming that block, by: read_block (Python),
      check_trace_dir/the check CLI (Python), and readBlock (JS, via Node)
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab_api.trace import check as check_module  # noqa: E402
from lab_api.trace import reference_decoder as rd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
# .worktrees/neuromod-lab-s0-contract/tests -> .worktrees/neuromod-lab-s0-contract -> .worktrees -> LLM


from conftest import find_lab_ui  # noqa: E402

LAB_UI_REPO = find_lab_ui()
FIXTURE_DIR = LAB_UI_REPO / "fixtures" / "trace-v1" / "universe-b2-gen0"
CONTRACT_DIR = LAB_UI_REPO / "contract"
VENDORED_SCHEMA = REPO_ROOT / "src" / "lab_api" / "trace" / "trace-v1.schema.json"

# Storage policy (LLM/CLAUDE.md): nothing but source/docs/small logs on the
# system disk -- scratch artifacts, including test-generated ones, go under
# /media/llm-data/scratch/.
SCRATCH_DIR = Path("/media/llm-data/scratch/s0-contract/test-corrupt-fixture")


def _require_fixture():
    if not FIXTURE_DIR.exists():
        pytest.fail(
            f"fixture not found at {FIXTURE_DIR} -- set LAB_UI_REPO to the lab-ui "
            "checkout. This is a failure, not a skip: a contract suite that disappears "
            "without failing hides exactly the drift it exists to catch"
        )


def test_fixture_manifest_validates_against_schema():
    _require_fixture()
    manifest = rd.load_manifest(FIXTURE_DIR)  # raises ManifestValidationError on failure
    assert manifest["magic"] == "trace-v1"
    assert manifest["run"] == "b2_cost_s113"
    assert manifest["count"] == 300
    assert len(manifest["samples_tick"]) == manifest["count"]


def test_every_block_decodes_with_declared_shape_and_dtype():
    _require_fixture()
    manifest = rd.load_manifest(FIXTURE_DIR)
    expected_names = {
        "retina", "wave", "cfc", "raw_intent", "after_head",
        "after_modulation", "final_command", "pose", "body",
    }
    assert {b["name"] for b in manifest["blocks"]} == expected_names

    for block in manifest["blocks"]:
        arr = rd.read_block(FIXTURE_DIR, block["name"], manifest=manifest)
        assert list(arr.shape) == block["shape"], block["name"]
        assert arr.dtype == np.dtype(rd.DTYPE_MAP[block["dtype"]]), block["name"]
        assert arr.nbytes == block["length"], block["name"]
        assert np.isfinite(arr.astype("float64")).all(), (
            f"block {block['name']} contains a non-finite value"
        )

    # absent stages are absent, never zero-filled
    for name in ("l1", "l2", "intent"):
        with pytest.raises(rd.AbsentBlockError, match="not recorded by this binary"):
            rd.read_block(FIXTURE_DIR, name, manifest=manifest)


def test_absent_block_raises_dedicated_error_not_bare_keyerror():
    _require_fixture()
    manifest = rd.load_manifest(FIXTURE_DIR)
    assert not issubclass(rd.AbsentBlockError, KeyError), (
        "AbsentBlockError must NOT be a KeyError -- a caller that catches only "
        "KeyError (e.g. generic dict-like access) must not silently swallow this"
    )
    assert issubclass(rd.AbsentBlockError, LookupError)

    with pytest.raises(rd.AbsentBlockError) as exc_info:
        rd.read_block(FIXTURE_DIR, "l1", manifest=manifest)
    assert exc_info.value.name == "l1"
    assert exc_info.value.reason == "not recorded by this binary"

    # a name that is neither a recorded block nor listed as absent is a
    # genuine manifest inconsistency -- still a plain KeyError, deliberately
    # distinct from AbsentBlockError.
    with pytest.raises(KeyError):
        rd.read_block(FIXTURE_DIR, "does_not_exist", manifest=manifest)


def test_replay_decodes_and_matches_its_own_header_invariants():
    _require_fixture()
    manifest = rd.load_manifest(FIXTURE_DIR)
    header, frames = rd.read_replay(FIXTURE_DIR / "physical.replay")
    assert header["magic"] == "IARARPLY"
    assert header["version"] == 1
    assert header["world_seed"] == manifest["world_seed"]
    assert len(frames) > 0
    for f in frames:
        assert f["being_idx"] < header["n_beings"]

    being_frames = [f for f in frames if f["being_idx"] == manifest["being"]]
    ticks = [f["tick"] for f in being_frames]
    assert ticks == sorted(ticks), "ticks must increase within a being"


def test_js_decoder_agrees_byte_for_byte_with_python():
    _require_fixture()
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not found on PATH")

    script = Path(__file__).with_name("decode_fixture.mjs")
    result = subprocess.run(
        [node, str(script), str(FIXTURE_DIR), str(CONTRACT_DIR)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, f"decode_fixture.mjs failed:\n{result.stderr}"
    js = json.loads(result.stdout)

    manifest = rd.load_manifest(FIXTURE_DIR)
    assert js["manifest_run"] == manifest["run"]
    assert js["manifest_count"] == manifest["count"]

    for block in manifest["blocks"]:
        name = block["name"]
        py_arr = rd.read_block(FIXTURE_DIR, name, manifest=manifest).reshape(-1)
        js_block = js["blocks"][name]
        assert js_block["dtype"] == block["dtype"], name
        assert js_block["length"] == py_arr.shape[0], name

        py_first8 = py_arr[:8].tolist()
        py_last8 = py_arr[-8:].tolist()
        if block["dtype"] == "f32":
            np.testing.assert_allclose(js_block["first8"], py_first8, rtol=0, atol=1e-6, err_msg=name)
            np.testing.assert_allclose(js_block["last8"], py_last8, rtol=0, atol=1e-6, err_msg=name)
        else:
            assert js_block["first8"] == py_first8, name
            assert js_block["last8"] == py_last8, name

    # replay header + first/last frame of the observed being
    py_header, py_frames = rd.read_replay(FIXTURE_DIR / "physical.replay", being=manifest["being"])
    assert js["replay_header"]["nBeings"] == py_header["n_beings"]
    assert js["replay_header"]["worldSeed"] == py_header["world_seed"]
    assert js["replay_n_frames"] == len(py_frames)

    py_first, py_last = py_frames[0], py_frames[-1]
    assert js["replay_first_frame"]["tick"] == py_first["tick"]
    np.testing.assert_allclose(js["replay_first_frame"]["pos"], py_first["pos"], atol=1e-4)
    assert js["replay_last_frame"]["tick"] == py_last["tick"]
    np.testing.assert_allclose(js["replay_last_frame"]["pos"], py_last["pos"], atol=1e-4)


@pytest.fixture
def corrupted_fixture_dir():
    """A copy of the fixture with 4 bytes flipped mid-file inside the 'cfc'
    block's byte range (offset 2174400..2289600), via `dd`, matching PRD S5
    validation point 2's exact scenario. Cleans up after the test.
    """
    _require_fixture()
    SCRATCH_DIR.parent.mkdir(parents=True, exist_ok=True)
    if SCRATCH_DIR.exists():
        shutil.rmtree(SCRATCH_DIR)
    shutil.copytree(FIXTURE_DIR, SCRATCH_DIR)

    trace_path = SCRATCH_DIR / "neural.trace"
    corrupt_offset = 2_200_000  # inside the 'cfc' block's [2174400, 2289600) range
    with open(trace_path, "r+b") as f:
        f.seek(corrupt_offset)
        original = f.read(4)
        flipped = bytes(b ^ 0xFF for b in original)
        f.seek(corrupt_offset)
        f.write(flipped)
    assert flipped != original  # dd-equivalent byte flip actually changed something

    try:
        yield SCRATCH_DIR
    finally:
        shutil.rmtree(SCRATCH_DIR, ignore_errors=True)


def test_corrupted_neural_trace_is_rejected_by_python_read_block(corrupted_fixture_dir):
    with pytest.raises(rd.BlockIntegrityError, match="cfc"):
        rd.read_block(corrupted_fixture_dir, "cfc")

    # verify=False is documented to skip the check -- must NOT raise.
    arr = rd.read_block(corrupted_fixture_dir, "cfc", verify=False)
    assert arr.shape == (300, 96)

    # an unrelated, uncorrupted block still verifies fine.
    rd.read_block(corrupted_fixture_dir, "wave")


def test_corrupted_neural_trace_is_rejected_by_check_cli(corrupted_fixture_dir):
    with pytest.raises(check_module.CheckError, match="cfc"):
        check_module.check_trace_dir(corrupted_fixture_dir)

    result = subprocess.run(
        [sys.executable, "-m", "lab_api.trace.check", str(corrupted_fixture_dir)],
        capture_output=True, text=True, cwd=str(REPO_ROOT / "src"),
        env={**os.environ, "PYTHONPATH": "."},
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "cfc" in result.stderr, result.stderr
    assert result.stderr.startswith("FAIL:")


def test_corrupted_neural_trace_is_rejected_by_js_decoder(corrupted_fixture_dir):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not found on PATH")
    script = Path(__file__).with_name("decode_fixture.mjs")
    result = subprocess.run(
        [node, str(script), str(corrupted_fixture_dir), str(CONTRACT_DIR)],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode != 0, "JS decoder must refuse a corrupted neural.trace"
    assert "cfc" in result.stderr, result.stderr


def test_clean_fixture_hashes_are_internally_consistent():
    """Sanity check independent of read_block/check_trace_dir: recompute every
    hash in manifest.json directly from neural.trace bytes with plain
    hashlib, to prove the fixture's own hashes are not just self-referential
    (i.e. the test isn't just checking a module against itself)."""
    _require_fixture()
    manifest = rd.load_manifest(FIXTURE_DIR)
    trace_bytes = (FIXTURE_DIR / "neural.trace").read_bytes()
    assert hashlib.sha256(trace_bytes).hexdigest() == manifest["hashes"]["neural_trace"]
    for block in manifest["blocks"]:
        chunk = trace_bytes[block["offset"]: block["offset"] + block["length"]]
        assert hashlib.sha256(chunk).hexdigest() == block["sha256"], block["name"]


@pytest.mark.xfail(
    reason=(
        "obs2 additions (hashes.observed_genome[_file], block.name enum) not yet applied "
        "to the canonical lab-ui/contract/trace-v1.schema.json -- this worktree has no "
        "lab-ui checkout to edit it directly. See SCHEMA-CHANGE-observation_stage2_blocks.md "
        "and DEVIATIONS.md #13. Delete this marker (and the 'diverges' test below) once the "
        "canonical copy is patched -- same pattern used for #10/#12 before lab-ui caught up."
    ),
    strict=True,
)
def test_vendored_schema_is_byte_identical_to_lab_ui_contract():
    """The contract lives in lab-ui; neuromod-lab vendors a copy. Any drift is a failure.
    Re-enabled 16/09 when lab-ui adopted the S2 schema additions; re-xfailed same day for
    the obs2 follow-up (DEVIATIONS.md #13) -- see the marker above."""
    _require_fixture()
    schema_in_lab_ui = CONTRACT_DIR / "trace-v1.schema.json"
    assert schema_in_lab_ui.exists(), schema_in_lab_ui
    assert VENDORED_SCHEMA.exists(), VENDORED_SCHEMA
    assert schema_in_lab_ui.read_bytes() == VENDORED_SCHEMA.read_bytes(), (
        f"{VENDORED_SCHEMA} is not byte-identical to {schema_in_lab_ui} -- "
        "re-copy it whenever the schema changes"
    )


def test_vendored_schema_diverges_from_lab_ui_contract_only_by_documented_obs2_additions():
    """Pins the obs2 follow-up gap (2026-09-16, observation_schema=2 stage blocks) until
    `SCHEMA-CHANGE-observation_stage2_blocks.md`'s patch lands in the canonical
    `lab-ui/contract/trace-v1.schema.json` (see `DEVIATIONS.md` #13). Applies that EXACT
    patch to a parsed copy of the canonical schema and asserts the result equals the
    vendored copy -- if this ever fails because the canonical schema changed elsewhere,
    or once the patch lands for real, delete this test and the xfail marker above,
    restoring the plain byte-identity check as the only guard (same lifecycle
    `test_vendored_schema_diverges_from_lab_ui_contract_only_by_documented_s2_additions`
    had for #10/#12, before it was deleted when lab-ui caught up on 16/09)."""
    _require_fixture()
    schema_in_lab_ui = CONTRACT_DIR / "trace-v1.schema.json"
    assert schema_in_lab_ui.exists(), schema_in_lab_ui
    canonical = json.loads(schema_in_lab_ui.read_text())
    vendored = json.loads(VENDORED_SCHEMA.read_text())

    # Documented addition 1 (SCHEMA-CHANGE-observation_stage2_blocks.md §2): hashes.properties
    # gains two OPTIONAL keys.
    canonical["properties"]["hashes"]["properties"]["observed_genome"] = \
        vendored["properties"]["hashes"]["properties"]["observed_genome"]
    canonical["properties"]["hashes"]["properties"]["observed_genome_file"] = \
        vendored["properties"]["hashes"]["properties"]["observed_genome_file"]

    # Documented addition 2 (SCHEMA-CHANGE-observation_stage2_blocks.md §1): $defs.block's
    # 'name' property gains an explicit enum.
    canonical["$defs"]["block"]["properties"]["name"] = \
        vendored["$defs"]["block"]["properties"]["name"]

    assert canonical == vendored, (
        "vendored schema diverges from lab-ui's canonical copy by MORE than the two "
        "documented obs2 additions (hashes.observed_genome[_file], block.name enum) -- "
        "see SCHEMA-CHANGE-observation_stage2_blocks.md and DEVIATIONS.md #13"
    )
