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
============================= test session starts ==============================
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
