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

## S2 — trace producer (`lab_api.trace.producer`/`produce`) + Universe genome/track export

# TESTING.md — S2: trace producer + Universe `genome_export`/`brain_step`/`track_export`

Slice S2 (`lab-ui/PRD.md` §8) adds `neuromod-lab/src/lab_api/trace/producer.py`
(`produce()`), its CLI `neuromod-lab/src/lab_api/trace/produce.py`
(`python -m lab_api.trace.produce`), and three CPU-only Rust binaries in the Universe
worktree: `genome_export` (`.bin` genome -> `weights.json`), `brain_step` (CPU reference
forward through `raw_intent`, with ablation), `track_export` (track -> `track.json`).
This file is the exact commands run to verify all of it, with pasted output and exit
codes, per the worktree protocol (PRD §9.3).

Python: `/home/leonardo/projects/LLM/.venv-rocm/bin/python` (pytest 9.1.1, numpy already
present -- no installs). Rust: built only inside
`/home/leonardo/projects/LLM/.worktrees/universe-s2-pack` (never in `~/projects/LLM/Universe`).
Scratch: `/media/llm-data/scratch/s2-pack/`. Real data used: real finished runs under
`/media/llm-data/universe-runs/neuromod-lab-taxi/` (`b3_fixed_s31_t8005`, sparse,
`--resume`, 10 samples; `b5_ctrl_s31` generation 24, dense, no `--resume`, 750 samples),
copied into scratch before producing (never mutates the live run directories).

## 1. Rust: build

```
cd /home/leonardo/projects/LLM/.worktrees/universe-s2-pack
cargo build --release --bin genome_export --bin brain_step --bin track_export
```

Output (tail):
```
   Compiling universe v0.2.0 (/home/leonardo/projects/LLM/.worktrees/universe-s2-pack)
    Finished `release` profile [optimized] target(s) in 1.65s
```
Exit code: `0`. (`sha2 = "0.10.9"` was promoted from a transitive to a direct dependency
in `Cargo.toml` -- already resolved in `Cargo.lock` at that exact version via the Bevy
tree, no network fetch needed.)

## 2. Rust: unit tests (inline, next to each binary's own code)

```
cargo test --release --bin genome_export --bin brain_step --bin track_export
```

Output (summary):
```
running 6 tests   (brain_step)
test result: ok. 6 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 3 tests   (genome_export)
test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

running 3 tests   (track_export)
test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```
Exit code: `0`.

## 3. Rust: regression -- the two pre-existing suites this slice must not break

```
cargo test --release --bin gpu_evolve
cargo test --release --lib
```

Output (tail of each):
```
test result: ok. 119 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out   (gpu_evolve)
test result: ok. 480 passed; 0 failed; 16 ignored; 0 measured; 0 filtered out  (--lib)
```
Exit code: `0` for both. (16 ignored are the GPU parity tests, unaffected -- no GPU on
this task per the "Where" rules.) The only library change this slice made was extracting
`CfCCell::quantize_state_i8` out of `CfCCell::update`'s last line (`src/cfc.rs`) --
same formula, now a named, reusable function; `cargo build` also picked up the new
`sha2` direct dependency.

## 4. Rust: genome_export smoke against the S0 fixture's genome

```
./target/release/genome_export \
  /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0/genome.bin \
  /media/llm-data/scratch/s2-pack/weights_b2gen0.json
```
Output:
```
genome_export: wrote /media/llm-data/scratch/s2-pack/weights_b2gen0.json (18 stages, genome sha256 29c9a51b5daa0863c05fc98b509fd706eeac16180da4b3fa00b136c41c117045)
```
Exit code: `0`. `genome_sha256` matches the fixture's own `manifest.json`
`hashes.checkpoint` (`29c9a51b...c117045`) exactly.

18 stages, shapes: `l1 [96,192]`, `l2 [48,96]`, `kan_knots [3,12]`, `slow_d1_weights
[16,64]`, `slow_d1_bias [16]`, `slow_d2_weights [3,16]`, `slow_d2_bias [3]`, `tau [96]`,
`sensors [6]`, `neuron_alpha_l1 [96]`, `neuron_alpha_l2 [48]`, `neuron_period_l1 [96]`,
`neuron_threshold_l1 [96]`, `neuron_activation_l1 [96]`, `neuron_activation_l2 [48]`,
`gates_w [16]`, `hip [29]`, `fly [0]` (this genome carries no fly-map block).
`brain_flow` = the 18 names above, in that order (genome_io.rs's own on-disk block
order -- see `docs/LAB-UI-S2-GENOME-EXPORT.md` for why, and why that is NOT the per-tick
kernel dispatch order).

## 5. Rust: brain_step acceptance -- reference forward vs. recorded `raw_intent`, 50 samples

Samples built from the fixture's own `wave`/`cfc`/`raw_intent` blocks (ticks 16..800):

```
./target/release/brain_step --batch \
  /home/leonardo/projects/LLM/lab-ui/fixtures/trace-v1/universe-b2-gen0/genome.bin \
  /media/llm-data/scratch/s2-pack/samples_b2gen0_50.json \
  /media/llm-data/scratch/s2-pack/brain_step_report_b2gen0.json
```
Output:
```
brain_step --batch: wrote /media/llm-data/scratch/s2-pack/brain_step_report_b2gen0.json (50 samples, 50 compared, max_abs_error=1.6592474)
```
Exit code: `0`.

**Result: max abs error 1.659, mean 0.835, median 0.811, min 0.395** (over 3
`raw_intent` channels x 50 samples, each channel in [-1,1]). This does NOT match well,
and was NOT tuned to match better -- see `docs/LAB-UI-S2-GENOME-EXPORT.md` in the
Universe worktree for the full diagnosis. Short version: the fixture's genome
(`evolve_best_gen0000.bin`, the fitness champion) is not verified to be the same
individual as the recorded being (population slot 0, run had no `--resume` --
`lab-ui/contract/DEVIATIONS.md` #2), which is the most likely dominant cause; two
smaller, documented approximations (no persistent output fatigue; P1.7 neuron
mechanisms not applied) also contribute an unknown but smaller amount.

## 6. Python: syntax / compile check

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s2-pack
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m py_compile \
  src/lab_api/trace/producer.py src/lab_api/trace/produce.py \
  src/lab_api/trace/check.py src/lab_api/trace/reference_decoder.py
echo "compiled OK"
```
Output: `compiled OK`. Exit code: `0`.

## 7. Python: full test suite

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s2-pack
/home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/ -v
```

Output (tail):
```
tests/test_trace_producer.py::test_produce_sparse_resumed_run_validates_and_decodes PASSED [ 74%]
tests/test_trace_producer.py::test_check_cli_exits_zero_on_produced_trace PASSED [ 77%]
tests/test_trace_producer.py::test_js_decoder_agrees_with_python_decoder PASSED [ 80%]
tests/test_trace_producer.py::test_idempotent_refuses_then_force_rebuilds_byte_identically PASSED [ 83%]
tests/test_trace_producer.py::test_produce_dense_unresumed_run_champion_profile PASSED [ 87%]
tests/test_trace_producer.py::test_summary_profile_has_zero_blocks_and_still_validates PASSED [ 90%]
tests/test_trace_producer.py::test_event_profile_windows_around_events PASSED [ 93%]
tests/test_trace_producer.py::test_register_writes_trace_row_into_a_scratch_db PASSED [ 96%]
tests/test_trace_producer.py::test_producer_output_agrees_with_s0_fixture_on_shared_blocks SKIPPED [100%]

============= 29 passed, 1 skipped, 1 xfailed in 91.71s (0:01:31) ==============
```
Exit code: `0`.

- The 1 skip is `test_producer_output_agrees_with_s0_fixture_on_shared_blocks`: the S0
  fixture's source run (`b2_cost_s113`) is no longer on disk -- skipped with a clear
  message, per the task brief, not silently passed.
- The 1 xfail is `test_vendored_schema_is_byte_identical_to_lab_ui_contract`, kept only
  for reference; see `test_vendored_schema_diverges_from_lab_ui_contract_only_by_documented_s2_additions`
  (passing) and `src/lab_api/DEVIATIONS.md` #2/#3/#9/#10.

## 8. Manual smoke: produce, validate, decode with both decoders (sparse run)

```
cd /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s2-pack/src
PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.produce \
  /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005 --gen 0 --profile champion --no-db
```
Output:
```
OK: /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005/trace/gen0000/being00/champion (--no-db, not registered)
```
Exit code: `0`.

```
PYTHONPATH=. /home/leonardo/projects/LLM/.venv-rocm/bin/python -m lab_api.trace.check \
  /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005/trace/gen0000/being00/champion
```
Output:
```
OK: manifest.json and 9 blocks in .../champion/neural.trace match their declared sha256
```
Exit code: `0`.

JS cross-check (needs a scratch "contract dir" combining the real `decoder.js`/
`replay.js` with the VENDORED schema -- see `src/lab_api/DEVIATIONS.md` #9/#10 for why
the canonical `lab-ui/contract` schema cannot be used as-is here):
```
mkdir -p /media/llm-data/scratch/s2-pack/contract-vendored
cd /media/llm-data/scratch/s2-pack/contract-vendored
ln -sf /home/leonardo/projects/LLM/lab-ui/contract/{decoder.js,replay.js,package.json} .
ln -sf /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s2-pack/src/lab_api/trace/trace-v1.schema.json .
node /home/leonardo/projects/LLM/.worktrees/neuromod-lab-s2-pack/tests/decode_fixture.mjs \
  /media/llm-data/universe-runs/neuromod-lab-taxi/b3_fixed_s31_t8005/trace/gen0000/being00/champion \
  /media/llm-data/scratch/s2-pack/contract-vendored
```
Output (truncated, one JSON line): `{"manifest_run":"b3_fixed_s31_t8005","manifest_count":10,"blocks":{"retina":{...` --
every block decodes with the manifest's declared length; the script's own
`verifyNeuralTraceHash` call did not throw. Exit code: `0`.

## 9. Manual smoke: idempotency

```
PYTHONPATH=. python -m lab_api.trace.produce .../b5_ctrl_s31 --gen 24 --profile champion --no-db   # first: OK
PYTHONPATH=. python -m lab_api.trace.produce .../b5_ctrl_s31 --gen 24 --profile champion --no-db   # second, no --force
```
Second call's output:
```
UP TO DATE: .../b5_ctrl_s31/trace/gen0024/being00/champion (use --force to rebuild)
```
Then with `--force`: `neural.trace` and `manifest.json`'s `hashes` were verified
byte-identical to the pre-force copy (`sha256sum` before/after, `diff` empty). Exit
code `0` throughout.

## 10. Manual smoke: `--all-finished` at scale

```
PYTHONPATH=. python -m lab_api.trace.produce --all-finished \
  /media/llm-data/universe-runs/neuromod-lab-taxi --db /media/llm-data/scratch/s2-pack/lab_test.db
```
Output (tail):
```
--all-finished: 67 produced, 12 skipped (not finished), out of 79 candidates
```
Exit code: `0`. 0 `FAIL` lines across all 67. The 12 skips correctly include every
in-flight run present at the time (`b5_long_*`, `b5_rand_*`, `b5_rot_*`) -- verified by
grep: `SKIP b5_rot_s77: not finished (or no population_gen*.json yet)` appears in the
output; none of those in-flight runs' directories were ever written to (the skip happens
before any file is touched).

## What is NOT tested here

- The FastAPI routes (`GET /api/trace/...`) and the browser-side loader/panels: S1/S3,
  not S2.
- `event` profile windowing against a run with an `impact` event (none of the runs
  produced during this task happened to have one for the observed being) -- `brake_on`/
  `brake_off`/`gear`/`lap`/`near_wall` were all exercised on real data (`b3_fixed_s31_t8005`
  had 4 laps and 875 events total).
- Track rotation (`args.tracks` with more than one seed) -- see `DEVIATIONS.md` #11
  (was #8 before the S4 addition renumbered it); no rotating run was available/finished
  during this task (`b5_rot_*` explicitly off-limits, in flight).
