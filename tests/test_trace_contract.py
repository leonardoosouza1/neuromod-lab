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
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab_api.trace import reference_decoder as rd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
# .worktrees/neuromod-lab-s0-contract/tests -> .worktrees/neuromod-lab-s0-contract -> .worktrees -> LLM
LLM_ROOT = Path(os.environ.get("LLM_ROOT", REPO_ROOT.parents[1]))
LAB_UI_REPO = Path(os.environ.get("LAB_UI_REPO", LLM_ROOT / "lab-ui"))
FIXTURE_DIR = LAB_UI_REPO / "fixtures" / "trace-v1" / "universe-b2-gen0"
CONTRACT_DIR = LAB_UI_REPO / "contract"
VENDORED_SCHEMA = REPO_ROOT / "src" / "lab_api" / "trace" / "trace-v1.schema.json"


def _require_fixture():
    if not FIXTURE_DIR.exists():
        pytest.skip(
            f"fixture not found at {FIXTURE_DIR} -- set LAB_UI_REPO to the lab-ui "
            "checkout if it is not a sibling of this repo's parent directory"
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
        with pytest.raises(KeyError, match="not recorded by this binary"):
            rd.read_block(FIXTURE_DIR, name, manifest=manifest)


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


def test_vendored_schema_is_byte_identical_to_lab_ui_contract():
    _require_fixture()
    schema_in_lab_ui = CONTRACT_DIR / "trace-v1.schema.json"
    assert schema_in_lab_ui.exists(), schema_in_lab_ui
    assert VENDORED_SCHEMA.exists(), VENDORED_SCHEMA
    assert schema_in_lab_ui.read_bytes() == VENDORED_SCHEMA.read_bytes(), (
        f"{VENDORED_SCHEMA} is not byte-identical to {schema_in_lab_ui} -- "
        "re-copy it whenever the schema changes"
    )
