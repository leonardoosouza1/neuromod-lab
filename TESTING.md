# TESTING — neuromod-lab slices

One section per merged slice of the lab-ui PRD; each section is the slice's own
TESTING.md as delivered and verified cold by a separate tester.

## S7 — lab_db extensions

# TESTING.md — S7: `lab_db` extensions

Slice S7 (`lab-ui/PRD.md` §8) adds four tables to `neuromod-lab/src/lab_db.py`
(`annotation`, `trace`, `queue_mirror`, `audit`), a `--battery` override for the
`ingest` CLI, and ingest support for the five `Universe/artifacts/*` run directories
Astra produced outside the runs root. This file is the exact commands run to verify
it, with the pasted output and exit codes, per the worktree protocol (PRD §9.3).

All commands use the project's one Python:
`/home/leonardo/projects/LLM/.venv-rocm/bin/python` (pytest 9.1.1 is present in that
venv — no install step needed). None of them touch `/media/llm-data/lab.db`; every
test and manual run below uses `tmp_path` (pytest) or a copy under
`/media/llm-data/scratch/s7-db/`.

## 1. Syntax / compile check

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s7-db
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m py_compile src/lab_db.py && echo "compiled OK"
```

Output:
```
compiled OK
```
Exit code: `0`

## 2. Unit tests (pytest)

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s7-db
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_lab_db.py -v
```

Output:
```
============================= test session starts =======================

## S0 — trace-v1 contract

platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/leonardo/projects/LLM/.venv-rocm/bin/python
cachedir: .pytest_cache
rootdir: /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s7-db
plugins: anyio-4.14.1
collecting ... collected 11 items

tests/test_lab_db.py::test_schema_upgrade_adds_new_tables_and_keeps_old_rows PASSED [  9%]
tests/test_lab_db.py::test_annotation_round_trip PASSED                  [ 18%]
tests/test_lab_db.py::test_annotation_requires_existing_run PASSED       [ 27%]
tests/test_lab_db.py::test_trace_register_and_list PASSED                [ 36%]
tests/test_lab_db.py::test_mirror_queue_reads_spool_and_replaces_table PASSED [ 45%]
tests/test_lab_db.py::test_mirror_queue_never_writes_into_spool PASSED   [ 54%]
tests/test_lab_db.py::test_audit_stores_hash_not_payload PASSED          [ 63%]
tests/test_lab_db.py::test_audit_rejects_unknown_action PASSED           [ 72%]
tests/test_lab_db.py::test_ingest_universe_artifacts_never_crashes_and_battery_stays_null PASSED [ 81%]
tests/test_lab_db.py::test_ingest_universe_artifacts_with_battery_override PASSED [ 90%]
tests/test_lab_db.py::test_paired_excludes_unfinished_runs_by_default PASSED [100%]

============================== 11 passed in 0.45s ==============================
```
Exit code: `0`

`pytest` imports cleanly in the venv, so `tests/test_lab_db.py` is a normal pytest
file (fixtures: `tmp_path`, `pytest.raises`, `pytest.mark.skipif`) — the plain-assert
fallback described in the task was not needed.

What each test covers:

| test | covers |
|---|---|
| `test_schema_upgrade_adds_new_tables_and_keeps_old_rows` | a database with only the pre-S7 `run` table gets `annotation`/`trace`/`queue_mirror`/`audit` on `connect()`, and the pre-existing row survives |
| `test_annotation_round_trip` | `add_annotation` + `annotations()`, filtered by run and by (run, gen) |
| `test_annotation_requires_existing_run` | the `run_name` FK actually enforces (an annotation always points at something real) |
| `test_trace_register_and_list` | `register_trace` + `traces()`; re-registering the same (run, gen, being, profile) replaces, not duplicates |
| `test_mirror_queue_reads_spool_and_replaces_table` | 3 fake request files → pending / running / refused; state comes from folder + `estado/*.json` fase; re-mirroring after a file disappears drops its row (mirror, not history) |
| `test_mirror_queue_never_writes_into_spool` | the spool directory listing is byte-identical before/after `mirror_queue()` |
| `test_audit_stores_hash_not_payload` | the stored `payload_sha256` matches an independently computed hash; the payload's own content (a marker string) never appears in the row |
| `test_audit_rejects_unknown_action` | `action` is restricted to `launch\|cancel\|edit\|verdict\|annotation` |
| `test_ingest_universe_artifacts_never_crashes_and_battery_stays_null` | all 5 real `Universe/artifacts/*` dirs ingest without raising; `battery`/`arm`/`seed` are `NULL` (their manifests have a `command` argv, not universe_run.py's `args` dict, and their names have no `_s<seed>` suffix) |
| `test_ingest_universe_artifacts_with_battery_override` | `ingest_tree(..., battery='b1eval')` lands all 5 under battery `b1eval` |
| `test_paired_excludes_unfinished_runs_by_default` | regression guard for the decision recorded in `lab_db.py`'s own `paired()` docstring: an unfinished run's seed is excluded unless `include_running=True` |

The two artifact-ingest tests are `skipif`-guarded on `Universe/artifacts` existing, so
the file stays runnable on a machine without that tree.

## 3. Manual smoke: ingest `Universe/artifacts/*` into a scratch copy of the live DB

Never touches `/media/llm-data/lab.db` — copies it first.

```
cp /media/llm-data/lab.db /media/llm-data/scratch/s7-db/lab.db
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s7-db

# before: pre-S7 schema (proves the upgrade-in-place path, not just a fresh DB)
/home/leonardo/projects/LLM/.venv-rocm/bin/python -c "
import sqlite3
c = sqlite3.connect('/media/llm-data/scratch/s7-db/lab.db')
print(sorted(r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")))"

/home/leonardo/projects/LLM/.venv-rocm/bin/python src/lab_db.py --db /media/llm-data/scratch/s7-db/lab.db \
  ingest /home/leonardo/projects/LLM/Universe/artifacts --project universe-artifacts --battery b1eval

# after: new tables present
/home/leonardo/projects/LLM/.venv-rocm/bin/python -c "
import sqlite3
c = sqlite3.connect('/media/llm-data/scratch/s7-db/lab.db')
print(sorted(r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")))"

/home/leonardo/projects/LLM/.venv-rocm/bin/python src/lab_db.py --db /media/llm-data/scratch/s7-db/lab.db \
  list --battery b1eval
```

Output:
```
['artifact', 'being_gen', 'driving', 'generation', 'prediction', 'run']

ingested 5 run(s) into /media/llm-data/scratch/s7-db/lab.db
    b1-s77-heldout-8200
    b1-s77-heldout-9001
    b1-s77-horizon-30000
    b1-s77-horizon-30000-lvp
    b1-s77-horizon-30000-lvp2

['annotation', 'artifact', 'audit', 'being_gen', 'driving', 'generation', 'prediction', 'queue_mirror', 'run', 'sqlite_sequence', 'trace']

name                       project             battery  arm  seed  status   gens_complete  ...
-------------------------  ------------------  -------  ---  ----  -------  -------------  ...
b1-s77-heldout-8200        universe-artifacts  b1eval   -    -     running  1              ...
b1-s77-heldout-9001        universe-artifacts  b1eval   -    -     running  1              ...
b1-s77-horizon-30000       universe-artifacts  b1eval   -    -     running  0              ...
b1-s77-horizon-30000-lvp   universe-artifacts  b1eval   -    -     running  0              ...
b1-s77-horizon-30000-lvp2  universe-artifacts  b1eval   -    -     running  1              ...
```
(columns trimmed for width; full `list` output has all `run` columns.) Exit code of
the ingest command: `0`.

Live DB check — untouched:
```
md5sum /media/llm-data/lab.db      # unchanged before/after this whole session
stat -c '%Y %n' /media/llm-data/lab.db   # mtime unchanged before/after
```
Both confirmed identical before and after every command in this file.

**Known deviation, not introduced by S7:** `status` reads `running` for all five,
including `b1-s77-heldout-8200`/`9001`/`lvp2` whose `manifest.json` shows
`simulation_exit: 0` (i.e. they finished). This is the pre-existing `status` formula
(`'finished' if gens_complete >= int(args.get('gens', 0) or 0) > 0 else 'running'`,
unchanged by this slice) applied to a manifest that has no `args` dict (only a raw
`command` argv, because these were produced by calling `gpu_evolve` directly rather
than through `universe_run.py`) — `args.get('gens', 0)` is `0`, so the condition never
reaches `finished`. The task asked only that `battery`/`arm`/`seed` come from
`manifest.json:args` when present and stay `NULL` otherwise, never crash — verified
above — not that `status` be re-derived for argv-only manifests. Flagged here rather
than silently patched, per the existing-contract-wins rule.

## 4. Manual smoke: the Python API (annotation, trace, queue_mirror, audit)

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s7-db
/home/leonardo/projects/LLM/.venv-rocm/bin/python - <<'PYEOF'
import sys, os, json, tempfile
sys.path.insert(0, 'src')
import lab_db

dbpath = '/media/llm-data/scratch/s7-db/api-smoke.db'
if os.path.exists(dbpath): os.remove(dbpath)
db = lab_db.connect(dbpath)
db.execute("INSERT INTO run (name, project, out_dir, status, ingested) "
           "VALUES ('r1','universe','/tmp/r1','finished', datetime('now'))")
db.commit()

aid = lab_db.add_annotation(db, 'r1', 'brake fires late', gen=5, author='leo')
print('add_annotation ->', aid)
print('annotations(run=r1) ->', [dict(r) for r in lab_db.annotations(db, run='r1')])

lab_db.register_trace(db, 'r1', 0, 0, 'summary', '/data/r1/trace/gen0000/being00/summary',
                       schema_version=1, manifest_sha256='deadbeef', size_bytes=12345)
print('traces(run=r1) ->', [dict(r) for r in lab_db.traces(db, run='r1')])

aud_id = lab_db.audit(db, 'leo', 'launch', {'gens': 30, 'seed': 77}, note='B1 relaunch')
print('audit row ->', dict(db.execute('SELECT * FROM audit WHERE id=?', (aud_id,)).fetchone()))

with tempfile.TemporaryDirectory() as spool:
    for sub in ('pedidos', 'feitos', 'recusados', 'estado'):
        os.makedirs(os.path.join(spool, sub))
    json.dump({'id': 'pend1', 'script': 'universe_run', 'out': 'pend1', 'args': {'seed': 1}},
               open(os.path.join(spool, 'pedidos', 'pend1.json'), 'w'))
    json.dump({'id': 'run1', 'script': 'universe_run', 'out': 'run1', 'args': {'seed': 2}},
               open(os.path.join(spool, 'pedidos', 'run1.json'), 'w'))
    json.dump({'id': 'run1', 'fase': 'rodando'}, open(os.path.join(spool, 'estado', 'run1.json'), 'w'))
    json.dump({'id': 'bad1', 'script': 'nope', 'out': 'x', 'args': {}},
               open(os.path.join(spool, 'recusados', 'bad1.json'), 'w'))
    n = lab_db.mirror_queue(db, spool=spool)
    print('mirror_queue ->', n, 'rows')
    print([dict(r) for r in db.execute('SELECT id,state,script FROM queue_mirror ORDER BY id')])
PYEOF
```

Output:
```
add_annotation -> 1
annotations(run=r1) -> [{'id': 1, 'run_name': 'r1', 'gen': 5, 'tick': None, 'author': 'leo', 'text': 'brake fires late', 'created': '2026-09-16 00:45:49'}]
traces(run=r1) -> [{'run_name': 'r1', 'gen': 0, 'being': 0, 'profile': 'summary', 'schema_version': 1, 'path': '/data/r1/trace/gen0000/being00/summary', 'manifest_sha256': 'deadbeef', 'bytes': 12345, 'produced': '2026-09-16 00:45:49'}]
audit row -> {'id': 1, 'when': '2026-09-16 00:45:49', 'who': 'leo', 'action': 'launch', 'payload_sha256': 'b33db2a9bebd524a5eaa5e61270aaec376b8badffa7bc1110171cbaa3ce78874', 'note': 'B1 relaunch'}
mirror_queue -> 3 rows
[{'id': 'bad1', 'state': 'refused', 'script': 'nope'}, {'id': 'pend1', 'state': 'pending', 'script': 'universe_run'}, {'id': 'run1', 'state': 'running', 'script': 'universe_run'}]
```
Exit code: `0`

(`api-smoke.db` was removed after this run — scratch files here are throwaway, per
the storage policy the project already used for `/media/llm-data/scratch/`.)

## Scope note

`lab_db.py`'s docstring contract (SQLite standard library, database indexes not owns,
idempotent ingestion, `prediction.status` written only by hand or ✓/✗) was preserved
as-is; nothing in the PRD contradicted it for this slice. The only judgment call was
`status` for argv-only manifests (§3 above), and the existing formula was left
untouched rather than guessed at.
=======
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
## S1 — API

# TESTING.md — S1: FastAPI backend (`src/lab_api/`)

Slice S1 (`lab-ui/PRD.md` §8) replaces `src/lab_api.py` (stdlib server) at
feature parity plus everything else PRD §7 lists, as a FastAPI app in
`src/lab_api/`: `app.py`/`settings.py`/`auth.py`/`flags.py`/`deps.py` and
`routes/{db,queue,trace,counterfactual,auth_routes}.py`. `src/lab_api.py`
itself is untouched (parity first; removal is a later merge decision) and
`src/lab_api/trace/` (S0) is untouched.

All commands use the project's one Python:
`/home/leonardo/projects/LLM/.venv-rocm/bin/python`. `/media/llm-data/lab.db`
is never written by anything below -- every test and manual command uses a
copy under `/media/llm-data/scratch/s1-api/` or a pytest `tmp_path`. The
live nmd spool (`/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd/`) is
never written to either -- a battery may be actively using it; queue writes
below go to a scratch/temp spool.

## 0. New dependencies

`requirements-api.txt` lists the exact pins; installed one at a time with
`pip install --no-deps <pkg>==<version>` (never a bare `pip install fastapi`,
which would let pip resolve its own dependency tree and risk clobbering the
ROCm `torch` in this venv). Verified with `pip show` first which packages
were already present.

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/pip show fastapi starlette pydantic pydantic-core uvicorn h11 anyio sniffio idna click typing_extensions annotated-types 2>&1 | grep -E "^(Name|Version|WARNING)"
```

Installed (6 new, `--no-deps` each): `fastapi==0.115.6`, `starlette==0.41.3`,
`pydantic==2.10.3`, `pydantic-core==2.27.1`, `uvicorn==0.32.1`,
`sniffio==1.3.1`, `annotated-types==0.7.0`. Already present, untouched:
`h11==0.16.0`, `anyio==4.14.1`, `idna==3.18`, `click==8.4.2`,
`typing_extensions==4.15.0`, `pytest==9.1.1`, `httpx==0.28.1` (used by
`fastapi.testclient.TestClient`).

Verified the ROCm torch survived:

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/python -c "
import fastapi, starlette, pydantic, uvicorn, torch
print('fastapi', fastapi.__version__, '| starlette', starlette.__version__,
      '| pydantic', pydantic.VERSION, '| uvicorn', uvicorn.__version__, '| torch', torch.__version__)"
```

Output:
```
fastapi 0.115.6 | starlette 0.41.3 | pydantic 2.10.3 | uvicorn 0.32.1 | torch 2.9.1+rocm6.4
```
Exit code: `0`.

## 1. Syntax / compile check

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s1-api/src
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m py_compile \
  lab_api/settings.py lab_api/auth.py lab_api/flags.py lab_api/deps.py lab_api/app.py \
  lab_api/__main__.py lab_api/routes/db.py lab_api/routes/queue.py lab_api/routes/trace.py \
  lab_api/routes/counterfactual.py lab_api/routes/auth_routes.py && echo "compiled OK"
```

Output:
```
compiled OK
```
Exit code: `0`.

## 2. Unit + integration tests (pytest, `fastapi.testclient`)

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s1-api
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_lab_api.py -v
```

Output (run 2026-09-16, from this worktree, both `Universe/target/release/
pista_check` and the `lab-ui` fixture present so none of the 59 tests were
skipped -- the two `@REQUIRES_UNIVERSE`/`@REQUIRES_FIXTURE` skip guards exist
so this file still runs, with a reduced set, on a checkout missing either):

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- .venv-rocm/bin/python
rootdir: /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s1-api
plugins: anyio-4.14.1
collected 59 items

tests/test_lab_api.py::TestAuth::test_loopback_reads_and_writes_need_no_session PASSED
tests/test_lab_api.py::TestAuth::test_lan_read_without_session_is_401 PASSED
tests/test_lab_api.py::TestAuth::test_lan_login_wrong_password_is_401 PASSED
tests/test_lab_api.py::TestAuth::test_login_refused_in_loopback_mode PASSED
tests/test_lab_api.py::TestAuth::test_lan_login_then_read_succeeds PASSED
tests/test_lab_api.py::TestAuth::test_lan_write_without_csrf_header_is_403 PASSED
tests/test_lab_api.py::TestAuth::test_lan_write_with_csrf_header_succeeds_and_audits PASSED
tests/test_lab_api.py::TestAuth::test_sql_route_absent_under_lan PASSED
tests/test_lab_api.py::TestAuth::test_sql_route_present_in_loopback PASSED
tests/test_lab_api.py::TestAuth::test_sql_rejects_non_select PASSED
tests/test_lab_api.py::TestDbRoutes::test_batteries PASSED
tests/test_lab_api.py::TestDbRoutes::test_runs_filtered_by_battery_and_replays_count PASSED
tests/test_lab_api.py::TestDbRoutes::test_run_detail PASSED
tests/test_lab_api.py::TestDbRoutes::test_run_detail_404 PASSED
tests/test_lab_api.py::TestDbRoutes::test_predictions PASSED
tests/test_lab_api.py::TestDbRoutes::test_annotations_round_trip PASSED
tests/test_lab_api.py::TestDbRoutes::test_annotation_unknown_run_is_404 PASSED
tests/test_lab_api.py::TestDbRoutes::test_verdict_writes_and_audits PASSED
tests/test_lab_api.py::TestDbRoutes::test_verdict_bad_status_is_422 PASSED
tests/test_lab_api.py::TestDbRoutes::test_compare PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_writes_atomically_and_no_tmp_file_left PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_audits_launch PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_duplicate_id PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_bin_outside_snapshots PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_bin_in_champions_subdir PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_unknown_arm_flag PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_accepts_real_arm_flag_and_value_flag PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_switch_flag_with_false_value PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_value_flag_without_value PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_reserved_flag_name PASSED
tests/test_lab_api.py::TestQueueRoutes::test_post_rejects_invalid_track PASSED
tests/test_lab_api.py::TestQueueRoutes::test_get_queue_mirrors_pending_request PASSED
tests/test_lab_api.py::TestQueueRoutes::test_put_edits_pending_request_in_place PASSED
tests/test_lab_api.py::TestQueueRoutes::test_put_refuses_running_request PASSED
tests/test_lab_api.py::TestQueueRoutes::test_put_unknown_id_is_404 PASSED
tests/test_lab_api.py::TestQueueRoutes::test_delete_removes_pending_request PASSED
tests/test_lab_api.py::TestQueueRoutes::test_delete_refuses_running_request PASSED
tests/test_lab_api.py::TestQueueRoutes::test_delete_unknown_id_is_404 PASSED
tests/test_lab_api.py::TestTracksAndSnapshots::test_tracks_validate_real_seed PASSED
tests/test_lab_api.py::TestTracksAndSnapshots::test_snapshots_lists_binaries_and_champions PASSED
tests/test_lab_api.py::TestParsePistaCheck::test_no_defects_is_valid PASSED
tests/test_lab_api.py::TestParsePistaCheck::test_axis_off_track_is_invalid PASSED
tests/test_lab_api.py::TestParsePistaCheck::test_bottleneck_is_invalid PASSED
tests/test_lab_api.py::TestParsePistaCheck::test_null_variance_is_invalid PASSED
tests/test_lab_api.py::TestFlagRegistry::test_loads_real_registry_and_excludes_reserved PASSED
tests/test_lab_api.py::TestFlagRegistry::test_missing_file_raises PASSED
tests/test_lab_api.py::TestTraceRoutes::test_manifest_200 PASSED
tests/test_lab_api.py::TestTraceRoutes::test_manifest_404_when_not_produced PASSED
tests/test_lab_api.py::TestTraceRoutes::test_block_range_exact_byte_length PASSED
tests/test_lab_api.py::TestTraceRoutes::test_block_full_range_matches_manifest_length PASSED
tests/test_lab_api.py::TestTraceRoutes::test_block_hash_is_verified_and_cached PASSED
tests/test_lab_api.py::TestTraceRoutes::test_unknown_block_is_404 PASSED
tests/test_lab_api.py::TestTraceRoutes::test_absent_block_names_reason PASSED
tests/test_lab_api.py::TestTraceRoutes::test_replay_served_as_octet_stream PASSED
tests/test_lab_api.py::TestTraceRoutes::test_genome_served PASSED
tests/test_lab_api.py::TestTraceRoutes::test_events_served_as_json PASSED
tests/test_lab_api.py::TestTraceRoutes::test_weights_absent_with_reason PASSED
tests/test_lab_api.py::TestTraceRoutes::test_track_absent_with_reason PASSED
tests/test_lab_api.py::TestCounterfactual::test_returns_501 PASSED

============================== 59 passed in 3.83s ===============================
```
Exit code: `0`.

Full worktree regression (S0 + S7 + S1 together, nothing broke each other):

```
$ /home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/ -v
```
```
============================== 80 passed in 4.59s ===============================
```
Exit code: `0`.

What each test class covers:

| class | covers |
|---|---|
| `TestAuth` | loopback = fully open (reads and writes, no cookie); `--lan` = every route (reads included) needs a session (401 without one); wrong password is 401; `/api/login` itself refuses (400) in loopback mode (nothing to log into); a write without the CSRF header is 403 even with a valid session; a write with the CSRF header succeeds AND writes one `lab_db.audit` row; `/api/sql` is a 404 (route absent) under `--lan`, present and working in loopback, rejects non-SELECT |
| `TestDbRoutes` | every `/api/db/*` route (batteries/runs/run/predictions/annotations/verdict/annotation) plus `/api/compare`, against a small hermetic two-run dataset; `run/{name}` 404 for an unknown run; `annotation` 404 for an unknown run (FK enforced); verdict writes the DB, audits, and 422s on a bad status |
| `TestQueueRoutes` | POST writes exactly one file (no `.tmp` left over) with the correct pedido shape (`script: universe_run`, `args.bin`/`tracks` etc.); one `launch` audit row; 409 on a duplicate id; 422 for a `bin` outside `snapshots_root` (including one INSIDE `b1-champions/`, a real genome file, not an executable); 422 for an unknown arm flag; 201 for a REAL flag (`--no-neuron-memory`, a switch) and a real value flag (`sigma`) together, read back from the written pedido; 422 for a switch flag given `value: false` (daemon has no way to express "off" other than omitting the flag -- see `DEVIATIONS.md` #3); 422 for a value flag missing its value; 422 for a reserved flag name (`seed`, already a dedicated field); 422 for an invalid track (monkeypatches `validate_track` -- see `DEVIATIONS.md` #1 for why no real seed sampled in this session failed); GET mirrors a pending request via `lab_db.mirror_queue`; PUT edits a pending request IN PLACE (same filename) and 409s on a request marked `rodando` in `estado/`; DELETE removes a pending request and 409s the same way on a running one; both PUT and DELETE 404 on an unknown id |
| `TestTracksAndSnapshots` | `/api/tracks/validate?seed=8005` against the REAL `pista_check` binary (no GPU) returns `valid: true, issues: []`; `/api/snapshots` lists a fake binary and a fake champion genome from a scratch snapshots tree |
| `TestParsePistaCheck` | the output-classification function directly, against synthetic text for each defect marker (`AXIS OFF THE TRACK`, `BOTTLENECK`, `NULL VARIANCE`) and the clean case -- see `DEVIATIONS.md` #1 for why `AVISO` (the PRD's own wording) never appears in the real binary's current output |
| `TestFlagRegistry` | `flags.arm_flag_allow_list()` against the REAL `cli_flags.rs`: a real switch (`no-neuron-memory`, `takes_value=False`) and a real value flag (`sigma`, `True`) are present; `seed`/`out` (reserved, dedicated fields) are excluded; a missing file raises `FlagRegistryError` |
| `TestTraceRoutes` | manifest 200 on the S0 fixture (symlinked into a scratch `runs_root` at the PRD S5 path); manifest 404 `{"error":"not produced"}` for a run with no trace; a block range's byte length matches `(t1-t0) * row_bytes` exactly, and the full range matches the manifest's own `length`; the block-hash-verification cache (`trace._verified_blocks`) gets exactly one entry after two different tick-range requests to the same block (verified once, not per request); an unknown block name is 404; an absent block (`l1`) 404s naming its manifest `reason`; `replay`/`genome` are served as raw `application/octet-stream` bytes (the replay's magic bytes and the genome's exact byte count checked); `events` is served as JSON; `weights`/`track` (both legitimately absent from this fixture -- "produced by S2") 404 naming that reason |
| `TestCounterfactual` | the route is present and always answers `501` naming `S2` |

## 3. Manual smoke: a real `uvicorn` instance on a scratch port + curl

Never touches port 8130 (where a real instance might run) or the live spool.

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s1-api/src
mkdir -p /media/llm-data/scratch/s1-api/spool/{pedidos,estado,feitos,recusados}
mkdir -p /media/llm-data/scratch/s1-api/runs_root/b2_cost_s113/trace/gen0000/being00
ln -sfn /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0 \
  /media/llm-data/scratch/s1-api/runs_root/b2_cost_s113/trace/gen0000/being00/champion
cp /media/llm-data/lab.db /media/llm-data/scratch/s1-api/lab.db

PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api --port 8131 \
  --db /media/llm-data/scratch/s1-api/lab.db \
  --spool /media/llm-data/scratch/s1-api/spool \
  --runs-root /media/llm-data/scratch/s1-api/runs_root \
  --snapshots-root /media/llm-data/snapshots &
sleep 2

curl -s http://127.0.0.1:8131/api/health
curl -s http://127.0.0.1:8131/api/db/batteries | head -c 300
curl -s "http://127.0.0.1:8131/api/sql?q=select+1+as+one"
curl -s "http://127.0.0.1:8131/api/trace/b2_cost_s113/0/0/champion" | head -c 200
curl -s -o /dev/null -w "block bytes: %{size_download}\n" \
  "http://127.0.0.1:8131/api/trace/b2_cost_s113/0/0/champion/block/cfc?t0=0&t1=10"
curl -s "http://127.0.0.1:8131/api/tracks/validate?seed=8005"
curl -s "http://127.0.0.1:8131/api/snapshots" | head -c 300
curl -s -X POST "http://127.0.0.1:8131/api/counterfactual" \
  -H 'Content-Type: application/json' -d '{"trace":"x","tick":1,"remove":[]}' -w "\nHTTP %{http_code}\n"
curl -s -X POST http://127.0.0.1:8131/api/queue -H 'Content-Type: application/json' -d '{
  "id":"curlsmoke","bin":"/media/llm-data/snapshots/gpu_evolve-f5d203b",
  "gens":2,"ticks":100,"beings":4,"seed":1,"tracks":[8005]
}' -w "\nHTTP %{http_code}\n"
ls /media/llm-data/scratch/s1-api/spool/pedidos/
curl -s http://127.0.0.1:8131/api/queue
curl -s -X DELETE http://127.0.0.1:8131/api/queue/curlsmoke -w "\nHTTP %{http_code}\n"
ls /media/llm-data/scratch/s1-api/spool/pedidos/    # empty again
```

Actual output (run 2026-09-16):

```
{"ok":true,"lan":false}
[{"battery":"b5","runs":16,"finished":8,"arms":4,"seeds":4,"first_written":"2026-09-16T00:57:49+00:00","last_written":"2026-09-16T11:57:45+00:00"},{"battery":"b2","runs":8,"finished":0,"arms":2,"seeds":6,"first_written":"2026-09-16T00:38:28+00:00","last_written":"2026-09-16T00:39:23+00:00"},{"battery":"b1","runs":24,"finished":24,"arms":4,"seeds":6,"first_wr
[{"one":1}]
{"magic":"trace-v1","schema_version":1,"endian":"little","run":"b2_cost_s113","generation":0,"being":0,"being_selection":"fixed_population_slot_0 (--vision-be
block bytes: 3840
{"seed":8005,"width":28.0,"ate":600.0,"valid":true,"issues":[]}
{"binaries":[{"name":"gpu_evolve-f5d203b","path":"/media/llm-data/snapshots/gpu_evolve-f5d203b","bytes":11381640,"mtime":"2026-09-16T00:26:32","executable":true},{"name":"universe_pos_E1_20260813_1517.tar.gz","path":"/media/llm-data/snapshots/universe_pos_E1_20260813_1517.tar.gz","bytes":733964,"mtime":"2026-08-13T18:17:45","executable":false}],"champions":[{"name":"b1_fixed_s113.bin","path":"/med
{"detail":{"error":"needs the brain_step reference forward from S2"}}
HTTP 501
{"id":"curlsmoke","path":"/media/llm-data/scratch/s1-api/spool/pedidos/lab-ui_curlsmoke.json","pedido":{"id":"curlsmoke","script":"universe_run","out":"curlsmoke","env":{},"args":{"bin":"/media/llm-data/snapshots/gpu_evolve-f5d203b","gens":2,"ticks":100,"beings":4,"width":28.0,"seed":1,"tracks":[8005]}}}
HTTP 201
lab-ui_curlsmoke.json
[{"id":"curlsmoke","state":"pending","script":"universe_run","out":"curlsmoke","args_json":"{\"bin\": \"/media/llm-data/snapshots/gpu_evolve-f5d203b\", \"gens\": 2, \"ticks\": 100, \"beings\": 4, \"width\": 28.0, \"seed\": 1, \"tracks\": [8005]}","file_path":"/media/llm-data/scratch/s1-api/spool/pedidos/lab-ui_curlsmoke.json","seen":"2026-09-16 12:04:34"}]
{"removed":true,"id":"curlsmoke"}
HTTP 200
(pedidos/ empty)
```

Server stopped afterward (`kill` on its pid) and scratch spool/runs_root
removed; only `/media/llm-data/scratch/s1-api/lab.db` (a copy) was kept.
`/media/llm-data/lab.db`'s mtime was never touched by anything above --
every command here used `--db /media/llm-data/scratch/s1-api/lab.db`
explicitly. Note: `/api/db/batteries` shows a `b5` battery in this run --
that is real data ingested by something else in the system between the
scratch DB copy and this command, not written by this slice; S1 never
calls `lab_db.ingest_*`.

## What is NOT tested here

- `/ws/live` -- not this slice's route (S6).
- `POST /api/counterfactual`'s actual computation -- needs S2's `brain_step`
  reference forward; this slice only proves the route exists, is
  auth-gated, and answers 501 with the right message.
- The trace PRODUCER (`observation.jsonl` -> `neural.trace`) -- S2. This
  slice only serves a trace-v1 directory that already exists.
- `pista_check` classifying a REAL seed as invalid end-to-end -- every seed
  sampled while writing this slice came back clean; see `DEVIATIONS.md` #1
  for the seeds tried and how the "invalid track" path is covered instead
  (parser unit tests + a monkeypatched integration test).

## Deviations

See `src/lab_api/DEVIATIONS.md` -- five items: `pista_check`'s real defect
markers vs. the PRD's stale "AVISO" wording; confirming (not deviating)
that `--bin` validates against `/media/llm-data/snapshots/` by reading a
real live pedido; switch flags never accept `value: false`; every route
(not just writes) requires a session under `--lan`; `/api/snapshots`'
"binaries" is every top-level file, not a guessed subset.
