# Testing `lab_api.trace` (S0 contract)

Nothing to install. Uses `/home/leonardo/projects/LLM/.venv-rocm/bin/python`
only (already has `numpy` 2.4.4 and `pytest` 9.1.1; `jsonschema` is
deliberately NOT used -- see `lab-ui/contract/DEVIATIONS.md` #4). `node`
(v22.16.0) is used by several tests to cross-check the JS decoder.

## 1. Unit + cross-check test suite

From the repo root:

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_trace_contract.py -v
```

Actual output (run 2026-09-15, from
`/home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract`, after the
S0 hash/AbsentBlockError fixes):

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- .venv-rocm/bin/python
rootdir: /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract
plugins: anyio-4.14.1
collected 10 items

tests/test_trace_contract.py::test_fixture_manifest_validates_against_schema PASSED [ 10%]
tests/test_trace_contract.py::test_every_block_decodes_with_declared_shape_and_dtype PASSED [ 20%]
tests/test_trace_contract.py::test_absent_block_raises_dedicated_error_not_bare_keyerror PASSED [ 30%]
tests/test_trace_contract.py::test_replay_decodes_and_matches_its_own_header_invariants PASSED [ 40%]
tests/test_trace_contract.py::test_js_decoder_agrees_byte_for_byte_with_python PASSED [ 50%]
tests/test_trace_contract.py::test_corrupted_neural_trace_is_rejected_by_python_read_block PASSED [ 60%]
tests/test_trace_contract.py::test_corrupted_neural_trace_is_rejected_by_check_cli PASSED [ 70%]
tests/test_trace_contract.py::test_corrupted_neural_trace_is_rejected_by_js_decoder PASSED [ 80%]
tests/test_trace_contract.py::test_clean_fixture_hashes_are_internally_consistent PASSED [ 90%]
tests/test_trace_contract.py::test_vendored_schema_is_byte_identical_to_lab_ui_contract PASSED [100%]

============================== 10 passed in 0.39s ===============================
```
Exit code: `0`.

The three new tests (`test_corrupted_neural_trace_is_rejected_by_*`) copy
the fixture to `/media/llm-data/scratch/s0-contract/test-corrupt-fixture/`
(storage policy: nothing but source/docs/small logs on the system disk),
flip 4 bytes at a fixed offset inside the `cfc` block's byte range with
plain Python (`dd`-equivalent: `f.seek(offset); f.write(bytes(b^0xFF for b
in f.read(4)))`), and assert Python's `read_block`, the `check` CLI, and
Node's `readBlock` all refuse it and name `cfc` in the error. The fixture
copy is deleted again in the fixture's `finally` block.

This reads `lab-ui/fixtures/trace-v1/universe-b2-gen0/` and
`lab-ui/contract/` from the sibling `lab-ui` checkout
(`/home/leonardo/projects/LLM/lab-ui`, computed as
`tests/../../../lab-ui` from this worktree's path -- override with the
`LAB_UI_REPO` env var if your checkout is elsewhere). `tests/conftest.py`
puts `src/` on `sys.path` so no `PYTHONPATH` is needed for pytest.

## 2. `lab_api.trace.check` against a real run directory

**Note (2026-09-15, post-review):** the `b2_*` run directories (including
`b2_cost_s113`, the fixture's original source) were deleted at 21:56 when
that battery was replaced. The fixture itself is unaffected (real bytes
copied at cut time, no symlinks -- see
`lab-ui/fixtures/trace-v1/universe-b2-gen0/SOURCE.md`), but this
run-directory smoke test now points at runs that still exist.

This is PRD S5's validation point 1: every `observation.jsonl` sample must
match the run's own `driving.meta.json`. Requires `PYTHONPATH=src` since
this is a plain `python -m` invocation, not pytest:

```
$ cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract/src
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check \
    /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005
```

Actual output (run 2026-09-15; `b3_fixed_s31_t8005` is a finished, single-
generation run -- `--vision-every 2000`, hence only 10 samples -- picked
because it is done and will not be cleared mid-battery like an active
run):

```
OK: 10 samples in /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005/observation.jsonl match /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005/driving.meta.json
```
Exit code: `0`.

Alternative, against a dense, in-flight battery (32 beings, sample_every
16), to also demonstrate the "safe to run while a battery writes to it"
case:

```
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check \
    /media/llm-data/universe-runs/neuromod-lab-taxi/b5_ctrl_s113 --max-samples 300
```

Actual output (run 2026-09-15):

```
OK: 300 samples in /media/llm-data/universe-runs/neuromod-lab-taxi/b5_ctrl_s113/observation.jsonl match /media/llm-data/universe-runs/neuromod-lab-taxi/b5_ctrl_s113/driving.meta.json
```
Exit code: `0`.

Both `b3_*` and `b5_*` run directories predate the tester's review and are
independent of anything this task built; either may eventually be cleared
too (batteries get replaced) -- point the command at any current
`b*_*` directory under `/media/llm-data/universe-runs/neuromod-lab-taxi/`
that has `driving.meta.json` + `observation.jsonl` if both of these are
gone by the time you read this.

## 3. `lab_api.trace.check` against a trace-v1 directory (PRD S5 validation point 2)

Since the last review, `check` auto-detects a trace-v1 directory (a
`manifest.json` with `"magic": "trace-v1"`, vs. a raw run directory's
`observation.jsonl` + `driving.meta.json`) and validates the manifest
against the schema, then every block's sha256, then the whole
`neural.trace` file's sha256:

```
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check \
    /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0
```

Actual output (run 2026-09-15):

```
OK: manifest.json and 9 blocks in /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0/neural.trace match their declared sha256
```
Exit code: `0`.

## 4. `lab_api.trace.check` catches real mismatches (not just the happy path)

Observation-mode mismatch (a run directory whose `observation.jsonl` does
not match its own `driving.meta.json`):

```
$ mkdir -p /media/llm-data/scratch/s0-contract/fake_run
$ echo '{"retina_rows": 14, "retina_cols": 126, "wave_channels": 192, "fast_state_values": 96}' \
    > /media/llm-data/scratch/s0-contract/fake_run/driving.meta.json
$ python3 -c "
import json
sample = {'generation':0,'tick':16,'being':0,'retina':[0]*(14*126-1),'wave':[0]*192,
          'fast_state':[0.0]*96,'body':{'alive':True}}
open('/media/llm-data/scratch/s0-contract/fake_run/observation.jsonl','w').write(json.dumps(sample)+'\n')
"
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check /media/llm-data/scratch/s0-contract/fake_run
```

Actual output:

```
FAIL: sample 0 (tick=16): block 'retina' has 1763 elements, driving.meta.json declares retina_rows*retina_cols=14*126=1764
```
Exit code: `1`.

Trace-v1-mode mismatch (a corrupted `neural.trace`, `dd`-style 4-byte flip
inside the `cfc` block's range, on a scratch copy of the fixture):

```
$ cp -r /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0 /media/llm-data/scratch/s0-contract/corrupt-fixture
$ python3 -c "
with open('/media/llm-data/scratch/s0-contract/corrupt-fixture/neural.trace','r+b') as f:
    f.seek(2200000)
    data = f.read(4)
    f.seek(2200000)
    f.write(bytes(b ^ 0xFF for b in data))
"
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check /media/llm-data/scratch/s0-contract/corrupt-fixture
```

Actual output:

```
FAIL: block 'cfc': manifest sha256=6a191cfe4f0c18a595a7f76de71c1f2dd15b984325ce79880e08147b1cf8b5ae, actual sha256=a6fe9ba573d97d28b18b01e7153f704e1b8ff88fed8e87ebb201e6b1a3d04a2c
```
Exit code: `1`.

The Node decoder refuses the same corrupted copy too (naming `cfc` on
stderr, non-zero exit):

```
$ node tests/decode_fixture.mjs /media/llm-data/scratch/s0-contract/corrupt-fixture /home/leonardo/projects/LLM/lab-ui/contract
```
```
Error: block cfc: manifest sha256=6a191cfe4f0c18a595a7f76de71c1f2dd15b984325ce79880e08147b1cf8b5ae, actual sha256=a6fe9ba573d97d28b18b01e7153f704e1b8ff88fed8e87ebb201e6b1a3d04a2c
    at readBlock (file:///home/leonardo/projects/LLM/lab-ui/contract/decoder.js:223:13)
```
Exit code: `1`.

(All three of these exact checks are also automated in
`tests/test_trace_contract.py`'s `test_corrupted_neural_trace_is_rejected_by_*`
tests -- run manually here only to show the raw CLI/Node output.)

## What is NOT tested here

- `weights.json` / `track.json` production, the FastAPI routes, the trace
  producer itself (`observation.jsonl -> neural.trace`): all S2/S1, not S0.
  S0 only ships the contract (schema + reference decoders) and the fixture
  that was cut by hand from real data to exercise it -- see
  `lab-ui/fixtures/trace-v1/universe-b2-gen0/SOURCE.md` for exactly how.
- `jsonschema`-based validation: not installed, not used. `reference_decoder.py`'s
  own validator covers the subset of JSON Schema `trace-v1.schema.json` uses
  -- see its module docstring.
- Compression: every block's `compression` is `"none"` in schema_version 1;
  hashing/verification is defined only for that case.
