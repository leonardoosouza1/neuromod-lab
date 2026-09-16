"""Tests for the S7 additions to `lab_db.py`: annotation, trace, queue_mirror, audit,
and the Universe/artifacts ingest path. Runs with pytest (present in the project venv:
`.venv-rocm/bin/python -m pytest tests/test_lab_db.py -v`).

Every test uses a throwaway database under `tmp_path` (pytest's own per-test temp dir)
or `/media/llm-data/scratch/s7-db/`. NONE of them opens `/media/llm-data/lab.db` -- the
live database is read by a running panel and the project's storage policy forbids
writing scratch data into the system disk anyway. The one exception, the artifacts
ingest test, only READS `Universe/artifacts/*` and writes into a tmp_path database.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import lab_db  # noqa: E402

UNIVERSE_ARTIFACTS = '/home/leonardo/projects/LLM/Universe/artifacts'

# The five run directories Astra produced outside the runs root (lab-ui PRD §8, S7 row).
EXPECTED_ARTIFACT_RUNS = {
    'b1-s77-heldout-8200', 'b1-s77-heldout-9001', 'b1-s77-horizon-30000',
    'b1-s77-horizon-30000-lvp', 'b1-s77-horizon-30000-lvp2',
}

# The schema as it existed before S7 (run/generation/being_gen/driving/artifact/
# prediction only) -- used to prove that `lab_db.connect()` upgrades an EXISTING
# database in place, rather than assuming a fresh one. Trimmed to just `run`, the only
# table the upgrade test needs, plus enough columns for a real row.
LEGACY_SCHEMA = """
CREATE TABLE run (
    name           TEXT PRIMARY KEY,
    project        TEXT NOT NULL,
    battery        TEXT,
    arm            TEXT,
    seed           INTEGER,
    out_dir        TEXT NOT NULL,
    status         TEXT NOT NULL,
    written        TEXT,
    ingested       TEXT NOT NULL
);
"""


def _insert_run(db: sqlite3.Connection, name: str, battery: str | None = None,
                 arm: str | None = None, seed: int | None = None,
                 status: str = 'finished') -> None:
    db.execute(
        'INSERT INTO run (name, project, battery, arm, seed, out_dir, status, ingested)'
        " VALUES (?,?,?,?,?,?,?, datetime('now'))",
        (name, 'universe', battery, arm, seed, f'/tmp/{name}', status))
    db.commit()


def _insert_last5(db: sqlite3.Connection, run_name: str, gen: int,
                   brake_ticks: float, alive_ticks: float = 1000.0) -> None:
    """One `driving` row that `v_last5` will pick up (it takes the last five generations
    that exist per run, so a single gen=0 row is enough for a run with only one gen)."""
    db.execute(
        'INSERT INTO driving (run_name, gen, alive_ticks, brake_ticks, overlap_ticks,'
        ' impact_ticks, near_wall_ticks, stationary_ticks, reverse_ticks, contact_ticks,'
        ' distance_m, collision_energy_j, throttle_sum, brake_sum, speed_sum, beings,'
        ' min_last_tick) VALUES (?,?,?,?,0,0,0,0,0,0,0,0,0,0,0,1,?)',
        (run_name, gen, alive_ticks, brake_ticks, int(alive_ticks)))
    db.commit()


# ── schema upgrade ───────────────────────────────────────────────────────────────────

def test_schema_upgrade_adds_new_tables_and_keeps_old_rows(tmp_path):
    path = str(tmp_path / 'legacy.db')
    legacy = sqlite3.connect(path)
    legacy.executescript(LEGACY_SCHEMA)
    legacy.execute(
        "INSERT INTO run (name, project, out_dir, status, ingested)"
        " VALUES ('old_run', 'universe', '/tmp/old_run', 'finished', datetime('now'))")
    legacy.commit()
    legacy.close()

    db = lab_db.connect(path)
    tables = {r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    for new_table in ('annotation', 'trace', 'queue_mirror', 'audit'):
        assert new_table in tables, f'{new_table} missing after upgrade'

    # The pre-existing row survived the upgrade untouched.
    row = db.execute('SELECT * FROM run WHERE name = ?', ('old_run',)).fetchone()
    assert row is not None
    assert row['status'] == 'finished'

    # Re-running connect() on the now-upgraded database is a no-op (IF NOT EXISTS).
    db2 = lab_db.connect(path)
    tables2 = {r[0] for r in db2.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables2 == tables


# ── annotation ───────────────────────────────────────────────────────────────────────

def test_annotation_round_trip(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    _insert_run(db, 'r1')
    _insert_run(db, 'r2')

    aid = lab_db.add_annotation(db, 'r1', 'brake fires late', gen=5, author='leo')
    assert isinstance(aid, int) and aid > 0
    lab_db.add_annotation(db, 'r1', 'tick-level note', gen=5, tick=1200, author='agent-x')
    lab_db.add_annotation(db, 'r2', 'unrelated run', author='leo')

    all_r1 = lab_db.annotations(db, run='r1')
    assert len(all_r1) == 2
    assert {a['text'] for a in all_r1} == {'brake fires late', 'tick-level note'}

    scoped = lab_db.annotations(db, run='r1', gen=5)
    assert len(scoped) == 2
    assert all(a['gen'] == 5 for a in scoped)

    everything = lab_db.annotations(db)
    assert len(everything) == 3


def test_annotation_requires_existing_run(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    with pytest.raises(sqlite3.IntegrityError):
        lab_db.add_annotation(db, 'no_such_run', 'orphan note')


# ── trace index ──────────────────────────────────────────────────────────────────────

def test_trace_register_and_list(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    _insert_run(db, 'r1')

    lab_db.register_trace(db, 'r1', 0, 0, 'summary', '/data/r1/trace/gen0000/being00/summary',
                           schema_version=1, manifest_sha256='aaa', size_bytes=1000)
    lab_db.register_trace(db, 'r1', 0, 1, 'champion', '/data/r1/trace/gen0000/being01/champion',
                           schema_version=1, manifest_sha256='bbb', size_bytes=2000)

    rows = lab_db.traces(db, run='r1')
    assert len(rows) == 2
    assert {r['profile'] for r in rows} == {'summary', 'champion'}

    # Re-registering the same (run, gen, being, profile) replaces, never duplicates.
    lab_db.register_trace(db, 'r1', 0, 0, 'summary', '/data/r1/trace/gen0000/being00/summary-v2',
                           schema_version=1, manifest_sha256='ccc', size_bytes=1500)
    rows = lab_db.traces(db, run='r1')
    assert len(rows) == 2
    summary = next(r for r in rows if r['profile'] == 'summary')
    assert summary['manifest_sha256'] == 'ccc'
    assert summary['path'].endswith('summary-v2')


# ── queue mirror ─────────────────────────────────────────────────────────────────────

def test_mirror_queue_reads_spool_and_replaces_table(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    spool = tmp_path / 'spool'
    for sub in ('pedidos', 'feitos', 'recusados', 'estado'):
        (spool / sub).mkdir(parents=True)

    # Three fake request files covering the three states that differ by MECHANISM:
    # pending (in pedidos/, no running estado), running (in pedidos/, estado says
    # fase=rodando) and refused (in recusados/ -- folder alone decides this one).
    (spool / 'pedidos' / 'pend1.json').write_text(json.dumps(
        {'id': 'pend1', 'script': 'universe_run', 'out': 'pend1', 'args': {'seed': 1}}))
    (spool / 'pedidos' / 'run1.json').write_text(json.dumps(
        {'id': 'run1', 'script': 'universe_run', 'out': 'run1', 'args': {'seed': 2}}))
    (spool / 'estado' / 'run1.json').write_text(json.dumps(
        {'id': 'run1', 'fase': 'rodando', 'pid': 12345}))
    (spool / 'recusados' / 'bad1.json').write_text(json.dumps(
        {'id': 'bad1', 'script': 'not-whitelisted', 'out': 'x', 'args': {}}))

    n = lab_db.mirror_queue(db, spool=str(spool))
    assert n == 3

    rows = {r['id']: r for r in db.execute('SELECT * FROM queue_mirror')}
    assert rows['pend1']['state'] == 'pending'
    assert rows['run1']['state'] == 'running'
    assert rows['bad1']['state'] == 'refused'
    assert json.loads(rows['run1']['args_json']) == {'seed': 2}
    assert rows['pend1']['file_path'].endswith('pedidos/pend1.json')

    # It is a MIRROR: dropping a file and re-mirroring drops its row, no history kept.
    (spool / 'recusados' / 'bad1.json').unlink()
    n2 = lab_db.mirror_queue(db, spool=str(spool))
    assert n2 == 2
    ids = {r[0] for r in db.execute('SELECT id FROM queue_mirror')}
    assert 'bad1' not in ids


def test_mirror_queue_never_writes_into_spool(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    spool = tmp_path / 'spool'
    (spool / 'pedidos').mkdir(parents=True)
    (spool / 'pedidos' / 'p.json').write_text(json.dumps({'id': 'p', 'script': 's', 'out': 'o'}))
    before = {p: p.stat().st_mtime for p in spool.rglob('*')}
    lab_db.mirror_queue(db, spool=str(spool))
    after_listing = sorted(str(p) for p in spool.rglob('*'))
    assert after_listing == sorted(str(p) for p in before)  # nothing added, nothing removed


# ── audit ────────────────────────────────────────────────────────────────────────────

def test_audit_stores_hash_not_payload(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    payload = {'gens': 30, 'ticks': 12000, 'seed': 77, 'secret_looking_field': 'shhh'}
    aid = lab_db.audit(db, 'leo', 'launch', payload, note='B1 relaunch')
    row = db.execute('SELECT * FROM audit WHERE id = ?', (aid,)).fetchone()

    expected = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    assert row['payload_sha256'] == expected
    assert row['who'] == 'leo'
    assert row['action'] == 'launch'
    assert row['note'] == 'B1 relaunch'
    assert row['when'] is not None

    # The payload text itself never appears anywhere in the row.
    assert 'shhh' not in json.dumps(dict(row))


def test_audit_rejects_unknown_action(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    with pytest.raises(ValueError):
        lab_db.audit(db, 'leo', 'delete_everything', {})


# ── Universe/artifacts ingest ────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.path.isdir(UNIVERSE_ARTIFACTS),
                     reason='Universe/artifacts not present on this machine')
def test_ingest_universe_artifacts_never_crashes_and_battery_stays_null(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    found = {d for d in os.listdir(UNIVERSE_ARTIFACTS)
             if os.path.isdir(os.path.join(UNIVERSE_ARTIFACTS, d))}
    assert EXPECTED_ARTIFACT_RUNS <= found, \
        f'expected artifact dirs missing: {EXPECTED_ARTIFACT_RUNS - found}'

    for d in sorted(EXPECTED_ARTIFACT_RUNS):
        name = lab_db.ingest_run(db, os.path.join(UNIVERSE_ARTIFACTS, d),
                                  project='universe-artifacts')
        assert name == d, f'{d} did not ingest (manifest.json missing or unreadable?)'

    rows = {r['name']: r for r in lab_db.runs(db)}
    assert set(rows) == EXPECTED_ARTIFACT_RUNS
    for d, row in rows.items():
        # These names have no `_s<seed>` suffix and their manifest has no `args` dict
        # (it has a raw `command` argv instead) -- battery/arm/seed must stay NULL,
        # never raise.
        assert row['battery'] is None, d
        assert row['arm'] is None, d
        assert row['seed'] is None, d


@pytest.mark.skipif(not os.path.isdir(UNIVERSE_ARTIFACTS),
                     reason='Universe/artifacts not present on this machine')
def test_ingest_universe_artifacts_with_battery_override(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    names = lab_db.ingest_tree(db, UNIVERSE_ARTIFACTS, project='universe-artifacts',
                                battery='b1eval')
    assert set(names) == EXPECTED_ARTIFACT_RUNS

    rows = lab_db.runs(db, battery='b1eval')
    assert {r['name'] for r in rows} == EXPECTED_ARTIFACT_RUNS
    for r in rows:
        assert r['battery'] == 'b1eval'
        assert r['project'] == 'universe-artifacts'


# ── paired() regression guard (docstring: unfinished runs excluded by default) ───────

def test_paired_excludes_unfinished_runs_by_default(tmp_path):
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    # Two seeds, two arms. Seed 1 both arms finished. Seed 2's "fixed" run is still
    # running -- v_last5 would otherwise compare its partial generations against the
    # finished "nocost" run at the same seed (the effective-generations confound that
    # invalidated prediction 180, per lab_db.paired's own docstring).
    _insert_run(db, 'b1_fixed_s1', battery='b1', arm='fixed', seed=1, status='finished')
    _insert_run(db, 'b1_nocost_s1', battery='b1', arm='nocost', seed=1, status='finished')
    _insert_run(db, 'b1_fixed_s2', battery='b1', arm='fixed', seed=2, status='running')
    _insert_run(db, 'b1_nocost_s2', battery='b1', arm='nocost', seed=2, status='finished')

    _insert_last5(db, 'b1_fixed_s1', 0, brake_ticks=100.0)
    _insert_last5(db, 'b1_nocost_s1', 0, brake_ticks=50.0)
    _insert_last5(db, 'b1_fixed_s2', 0, brake_ticks=900.0)   # would dominate the mean
    _insert_last5(db, 'b1_nocost_s2', 0, brake_ticks=10.0)

    default = lab_db.paired(db, 'b1', 'fixed', 'nocost')
    assert default['n'] == 1
    assert [seed for seed, _ in default['per_seed']] == [1]

    interim = lab_db.paired(db, 'b1', 'fixed', 'nocost', include_running=True)
    assert interim['n'] == 2
    assert {seed for seed, _ in interim['per_seed']} == {1, 2}


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))


def test_run_name_parses_training_and_evaluation_runs():
    import lab_db
    cases = {
        'b1_legacy_nocost_s113': ('b1', 'legacy_nocost', '113', None),
        'b3_fixed_s31_t8005': ('b3', 'fixed', '31', '8005'),
        'b5_ctrl_s31_eval_t8200': ('b5', 'ctrl', '31', '8200'),
        'b1dup_nocost_s137': ('b1dup', 'nocost', '137', None),
    }
    for name, expected in cases.items():
        m = lab_db.RUN_NAME.match(name)
        assert m is not None, name
        assert (m.group('battery'), m.group('arm'), m.group('seed'), m.group('track')) == expected, name


def test_paired_never_crosses_tracks_or_training_with_evaluation(tmp_path):
    """Found 16/09: once `_t<track>` names parse, the same arm and seed exist on two tracks
    and in training; pairing must keep them apart."""
    import lab_db
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    def add(name, arm, seed, track, near_wall):
        db.execute("INSERT INTO run (name, project, battery, arm, seed, out_dir, status, ingested, eval_track)"
                   " VALUES (?, 'universe', 'bx', ?, ?, '/x', 'finished', datetime('now'), ?)",
                   (name, arm, seed, track))
        db.execute("INSERT INTO driving (run_name, gen, alive_ticks, brake_ticks, overlap_ticks, impact_ticks,"
                   " near_wall_ticks, stationary_ticks, reverse_ticks, contact_ticks, distance_m,"
                   " collision_energy_j, throttle_sum, brake_sum, speed_sum, beings, min_last_tick)"
                   " VALUES (?, 0, 100, 0, 0, 0, ?, 0, 0, 0, 1000, 0, 0, 0, 0, 1, 100)", (name, near_wall))
    add('bx_a_s1', 'a', 1, None, 10)
    add('bx_b_s1', 'b', 1, None, 30)
    add('bx_a_s1_t8200', 'a', 1, 8200, 50)
    add('bx_b_s1_t8200', 'b', 1, 8200, 90)
    add('bx_b_s1_t8005', 'b', 1, 8005, 0)
    db.commit()
    training = lab_db.paired(db, 'bx', 'a', 'b', 'near_wall_pct_alive')
    assert training['n'] == 1 and abs(training['mean'] - (10 - 30)) < 1e-9
    evaluation = lab_db.paired(db, 'bx', 'a', 'b', 'near_wall_pct_alive', eval_track=8200)
    assert evaluation['n'] == 1 and abs(evaluation['mean'] - (50 - 90)) < 1e-9
    assert lab_db.paired(db, 'bx', 'a', 'b', 'near_wall_pct_alive', eval_track=8005)['n'] == 0
    rows = db.execute("SELECT a.run_name, b.run_name FROM v_last5 a JOIN v_last5 b"
                      " ON a.seed = b.seed AND a.battery = b.battery AND a.eval_track IS b.eval_track"
                      " WHERE a.arm = 'a' AND b.arm = 'b' AND a.eval_track = 8200").fetchall()
    assert [tuple(r) for r in rows] == [('bx_a_s1_t8200', 'bx_b_s1_t8200')]


def test_connect_adds_eval_track_to_an_existing_database(tmp_path):
    import sqlite3
    import lab_db
    path = str(tmp_path / 'old.db')
    old = sqlite3.connect(path)
    old.executescript(lab_db.SCHEMA.replace(
        """    ingested       TEXT NOT NULL,
    eval_track     INTEGER                 -- set for frozen-champion evaluations (`_t<track>`)""",
        "    ingested       TEXT NOT NULL").replace(', r.eval_track', '').replace('seed, eval_track,', 'seed,'))
    old.execute("INSERT INTO run (name, project, out_dir, status, ingested) VALUES ('k', 'p', '/x', 'finished', 'now')")
    old.commit(); old.close()
    db = lab_db.connect(path)
    assert 'eval_track' in {r[1] for r in db.execute('PRAGMA table_info(run)')}
    assert db.execute("SELECT name FROM run").fetchone()[0] == 'k'
    db.execute("SELECT eval_track FROM v_last5").fetchall()


def test_drop_battery_reports_only_files_that_still_exist(tmp_path):
    import lab_db
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    kept = tmp_path / 'kept.replay'; kept.write_bytes(b'x' * 10)
    db.execute("INSERT INTO run (name, project, battery, out_dir, status, ingested)"
               " VALUES ('bz_a_s1', 'u', 'bz', ?, 'finished', 'now')", (str(tmp_path),))
    db.execute("INSERT INTO artifact VALUES ('bz_a_s1', 'replay', 0, ?, 10, '')", (str(kept),))
    db.execute("INSERT INTO artifact VALUES ('bz_a_s1', 'replay', 1, ?, 999, '')", (str(tmp_path / 'gone.replay'),))
    db.commit()
    report = lab_db.drop_battery(db, 'bz')
    assert report['runs_removed'] == 1
    assert [f['path'] for f in report['files']] == [str(kept)]
    assert report['missing_files'] == 1 and report['bytes'] == 10
