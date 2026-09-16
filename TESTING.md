# Testing `lab_api.trace` (S0 contract)

Nothing to install. Uses `/home/leonardo/projects/LLM/.venv-rocm/bin/python`
only (already has `numpy` 2.4.4 and `pytest` 9.1.1; `jsonschema` is
deliberately NOT used -- see `lab-ui/contract/DEVIATIONS.md` #4). `node`
(v22.16.0) is used by one test to cross-check the JS decoder.

## 1. Unit + cross-check test suite

From the repo root:

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_trace_contract.py -v
```

Actual output (run 2026-09-15, from
`/home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract`):

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- .venv-rocm/bin/python
rootdir: /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract
plugins: anyio-4.14.1
collected 5 items

tests/test_trace_contract.py::test_fixture_manifest_validates_against_schema PASSED [ 20%]
tests/test_trace_contract.py::test_every_block_decodes_with_declared_shape_and_dtype PASSED [ 40%]
tests/test_trace_contract.py::test_replay_decodes_and_matches_its_own_header_invariants PASSED [ 60%]
tests/test_trace_contract.py::test_js_decoder_agrees_byte_for_byte_with_python PASSED [ 80%]
tests/test_trace_contract.py::test_vendored_schema_is_byte_identical_to_lab_ui_contract PASSED [100%]

============================== 5 passed in 0.23s ===============================
```
Exit code: `0`.

This reads `lab-ui/fixtures/trace-v1/universe-b2-gen0/` and
`lab-ui/contract/` from the sibling `lab-ui` checkout
(`/home/leonardo/projects/LLM/lab-ui`, computed as
`tests/../../../lab-ui` from this worktree's path -- override with the
`LAB_UI_REPO` env var if your checkout is elsewhere). `tests/conftest.py`
puts `src/` on `sys.path` so no `PYTHONPATH` is needed for pytest.

## 2. `lab_api.trace.check` against a real, in-flight run directory

This is PRD S5's validation point 1: every `observation.jsonl` sample must
match the run's own `driving.meta.json`. Requires `PYTHONPATH=src` since
this is a plain `python -m` invocation, not pytest:

```
$ cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s0-contract/src
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check \
    /media/llm-data/universe-runs/neuromod-lab-taxi/b2_cost_s113 --max-samples 300
```

Actual output (run 2026-09-15, `b2_cost_s113` was still an in-flight
battery run at the time -- this is exactly the "safe to run while a battery
writes to it" case the tool is meant for):

```
OK: 300 samples in /media/llm-data/universe-runs/neuromod-lab-taxi/b2_cost_s113/observation.jsonl match /media/llm-data/universe-runs/neuromod-lab-taxi/b2_cost_s113/driving.meta.json
```
Exit code: `0`.

## 3. `lab_api.trace.check` catches a real mismatch (not just the happy path)

Proof that the check actually fails loudly, naming the block and both
values, rather than only ever printing OK:

```
$ mkdir -p /tmp/fake_run
$ echo '{"retina_rows": 14, "retina_cols": 126, "wave_channels": 192, "fast_state_values": 96}' \
    > /tmp/fake_run/driving.meta.json
$ python3 -c "
import json
sample = {'generation':0,'tick':16,'being':0,'retina':[0]*(14*126-1),'wave':[0]*192,
          'fast_state':[0.0]*96,'body':{'alive':True}}
open('/tmp/fake_run/observation.jsonl','w').write(json.dumps(sample)+'\n')
"
$ PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check /tmp/fake_run
```

Actual output:

```
FAIL: sample 0 (tick=16): block 'retina' has 1763 elements, driving.meta.json declares retina_rows*retina_cols=14*126=1764
```
Exit code: `1`.

## What is NOT tested here

- `weights.json` / `track.json` production, the FastAPI routes, the trace
  producer itself (`observation.jsonl -> neural.trace`): all S2/S1, not S0.
  S0 only ships the contract (schema + reference decoders) and the fixture
  that was cut by hand from real data to exercise it -- see
  `lab-ui/fixtures/trace-v1/universe-b2-gen0/SOURCE.md` for exactly how.
- `jsonschema`-based validation: not installed, not used. `reference_decoder.py`'s
  own validator covers the subset of JSON Schema `trace-v1.schema.json` uses
  -- see its module docstring.
