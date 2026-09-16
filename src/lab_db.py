"""The laboratory's run database: one SQLite file every agent, hook and panel can read.

Before this existed, each battery grew its own viewer -- six `replay_*` binaries in
Universe, five committed `painel-NN-*.html` files here, a live panel that dies with its
process -- and nothing survived a battery or could be queried across two of them.
Deleting an old battery meant archaeology over `rm -rf`.

The contract:

* **SQLite, standard library.** `import sqlite3` works in any agent, hook or skill with
  no server running and no package installed. `Universe/src/bin/impact.rs` already takes
  this route (it shells out to `python3` rather than depending on `rusqlite`).
* **The database indexes; it does not own.** Replays and genomes stay as files, because a
  row is the wrong place for 18 MB of binary; the `artifact` table keeps the path, the
  size and the checksum. The markdown ledgers stay the written record; `prediction` is an
  index into them so an agent can ask "which bets were refuted" without reading 58 KB of
  table.
* **Ingestion is idempotent.** Running it mid-battery and again at the end gives the same
  rows, so it is safe to call from a watch loop.

    python src/lab_db.py ingest /media/llm-data/universe-runs/neuromod-lab-taxi
    python src/lab_db.py list --battery b1
    python src/lab_db.py sql "select arm, avg(median_progress_m) from v_last5 group by arm"
    python src/lab_db.py rm b1 --yes          # rows only; files are named, never deleted

From Python:

    import lab_db
    db = lab_db.connect()
    for r in lab_db.runs(db, battery='b1'):
        print(r['name'], r['arm'], r['seed'], r['status'])
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
from typing import Any, Iterable

DEFAULT_PATH = '/media/llm-data/lab.db'

# `b1_legacy_nocost_s113`   -> battery b1, arm legacy_nocost, seed 113.
# `b3_fixed_s31_t8005`      -> battery b3, arm fixed, seed 31, eval_track 8005.
# `b5_ctrl_s31_eval_t8200`  -> battery b5, arm ctrl, seed 31, eval_track 8200.
# The track suffix marks a frozen-champion evaluation on that track. Without it in the
# pattern those runs parsed to battery/arm NULL (found by lab-ui S3, 16/09), and once parsed
# they must never be paired against a training run or against another track of the same seed.
RUN_NAME = re.compile(
    r'^(?P<battery>[a-z][a-z0-9]*)_(?P<arm>.+?)_s(?P<seed>\d+)(?P<eval>_eval)?(?:_t(?P<track>\d+))?$')

# Columns added after the first release of the schema; `connect()` adds them in place.
RUN_COLUMNS_ADDED = (('eval_track', 'INTEGER'),)

SCHEMA = """
CREATE TABLE IF NOT EXISTS run (
    name           TEXT PRIMARY KEY,
    project        TEXT NOT NULL,
    battery        TEXT,
    arm            TEXT,
    seed           INTEGER,
    out_dir        TEXT NOT NULL,
    status         TEXT NOT NULL,          -- running | finished | unknown
    written        TEXT,
    lab_commit     TEXT,
    script_sha256  TEXT,
    gens_requested INTEGER,
    gens_complete  INTEGER,
    ticks          INTEGER,
    beings         INTEGER,
    width          INTEGER,
    tracks         TEXT,
    wall_cost      REAL,
    impact_cost    REAL,
    command_json   TEXT,
    args_json      TEXT,
    config_json    TEXT,                   -- driving.meta.json: which code paths were live
    ingested       TEXT NOT NULL,
    eval_track     INTEGER                 -- set for frozen-champion evaluations (`_t<track>`)
);

-- One row per generation: the population summary the panel and most queries need.
CREATE TABLE IF NOT EXISTS generation (
    run_name           TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    gen                INTEGER NOT NULL,
    beings             INTEGER,
    median_progress_m  REAL,
    mean_progress_m    REAL,
    max_progress_m     REAL,
    median_distance_m  REAL,
    mean_speed_mps     REAL,
    impacts            INTEGER,
    collision_energy_j REAL,
    alive_ticks        INTEGER,
    dead               INTEGER,
    PRIMARY KEY (run_name, gen)
);

-- One row per being per generation, from population_gen*.json.
CREATE TABLE IF NOT EXISTS being_gen (
    run_name             TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    gen                  INTEGER NOT NULL,
    being                INTEGER NOT NULL,
    fitness              REAL,
    progress_m           REAL,
    distance_m           REAL,
    collision_energy_j   REAL,
    impact_count         INTEGER,
    alive_ticks          INTEGER,
    life_remaining_ticks REAL,
    life_exhausted       INTEGER,
    low_progress         INTEGER,
    fuel_remaining       REAL,
    hole_hits            INTEGER,
    x                    REAL,
    z                    REAL,
    PRIMARY KEY (run_name, gen, being)
);

-- Behaviour aggregates per generation, from driving.csv. Sums, never means of ratios:
-- the project has paid for that distinction (a per-frame mean once read +1.14 where the
-- aggregate read +0.045, and the sign of the conclusion changed with it).
CREATE TABLE IF NOT EXISTS driving (
    run_name           TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    gen                INTEGER NOT NULL,
    alive_ticks        REAL,
    brake_ticks        REAL,
    overlap_ticks      REAL,
    impact_ticks       REAL,
    near_wall_ticks    REAL,
    stationary_ticks   REAL,
    reverse_ticks      REAL,
    contact_ticks      REAL,
    distance_m         REAL,
    collision_energy_j REAL,
    throttle_sum       REAL,
    brake_sum          REAL,
    speed_sum          REAL,
    beings             INTEGER,
    min_last_tick      INTEGER,
    PRIMARY KEY (run_name, gen)
);

-- Files the database points at but never stores.
CREATE TABLE IF NOT EXISTS artifact (
    run_name TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    kind     TEXT NOT NULL,                -- replay | genome | log | csv
    gen      INTEGER,
    path     TEXT NOT NULL,
    bytes    INTEGER,
    sha256   TEXT,
    PRIMARY KEY (run_name, path)
);

-- An index into the markdown ledgers, which stay the written record.
CREATE TABLE IF NOT EXISTS prediction (
    code       TEXT NOT NULL,              -- B1, B1c, F6v, 191v...
    doc        TEXT NOT NULL,              -- path of the ledger it lives in
    project    TEXT NOT NULL,
    battery    TEXT,
    kind       TEXT,                       -- prediction | verdict (code ends in 'v')
    registered TEXT,
    status     TEXT,                       -- NULL until known: confirmed | refuted | partial
    summary    TEXT,
    PRIMARY KEY (doc, code)
);

-- A scientific note on a run, generation or tick. This is the record the PRD (lab-ui
-- §6) means by "annotations go to lab.db, never to localStorage": layout is per-browser
-- preference, an observation is data and outlives the browser that made it.
CREATE TABLE IF NOT EXISTS annotation (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_name TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    gen      INTEGER,
    tick     INTEGER,
    author   TEXT NOT NULL DEFAULT '',   -- a session user or an agent name
    text     TEXT NOT NULL,
    created  TEXT NOT NULL
);

-- An index into trace-v1 directories (the neural trace contract, lab-ui PRD §5). The
-- manifest format and the bytes on disk are slice S0's job; this table only lets an
-- agent or the API ask "does a trace already exist for (run, gen, being, profile)"
-- without walking the filesystem, and carries the hash that says whether it is stale.
CREATE TABLE IF NOT EXISTS trace (
    run_name        TEXT NOT NULL REFERENCES run(name) ON DELETE CASCADE,
    gen             INTEGER NOT NULL,
    being           INTEGER NOT NULL,
    profile         TEXT NOT NULL,       -- summary | champion | event | full
    schema_version  INTEGER,
    path            TEXT NOT NULL,
    manifest_sha256 TEXT,
    bytes           INTEGER,
    produced        TEXT NOT NULL,
    PRIMARY KEY (run_name, gen, being, profile)
);

-- A snapshot of the nmd spool (`neuromod-lab/scripts/nmd.py`) for the Queue panel. This
-- is a MIRROR, not history: `mirror_queue()` deletes and reinserts every row on each
-- call, because the ground truth is the files in `pedidos/`, `feitos/`, `recusados/` and
-- `estado/`, and nobody should have to diff two panel loads to know what changed on disk.
CREATE TABLE IF NOT EXISTS queue_mirror (
    id        TEXT PRIMARY KEY,          -- the request's own "id" field
    state     TEXT NOT NULL,             -- pending | running | done | refused
    script    TEXT,
    out       TEXT,
    args_json TEXT,
    file_path TEXT NOT NULL,
    seen      TEXT NOT NULL
);

-- One line per write the API performs (PRD §7: "one audit line in lab.db" per
-- launch/cancel/edit under --lan). The payload itself is never stored, only its hash:
-- the audit trail proves WHAT was sent without becoming a second, forever-growing copy
-- of every experiment schema or annotation text that passed through the API.
CREATE TABLE IF NOT EXISTS audit (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    "when"         TEXT NOT NULL,
    who            TEXT NOT NULL,
    action         TEXT NOT NULL,        -- launch | cancel | edit | verdict | annotation
    payload_sha256 TEXT NOT NULL,
    note           TEXT
);

CREATE INDEX IF NOT EXISTS idx_run_battery ON run(battery, arm, seed);
CREATE INDEX IF NOT EXISTS idx_gen_run     ON generation(run_name);
CREATE INDEX IF NOT EXISTS idx_being_run   ON being_gen(run_name, gen);
CREATE INDEX IF NOT EXISTS idx_annotation_run ON annotation(run_name, gen);
CREATE INDEX IF NOT EXISTS idx_queue_mirror_state ON queue_mirror(state);

-- The ruler most questions start from: the mean of the last five generations per run,
-- as ratios of sums. Kept as a view so the definition lives in exactly one place.
CREATE VIEW IF NOT EXISTS v_last5 AS
WITH ranked AS (
    SELECT d.*, r.battery, r.arm, r.seed, r.eval_track,
           ROW_NUMBER() OVER (PARTITION BY d.run_name ORDER BY d.gen DESC) AS from_end
      FROM driving d JOIN run r ON r.name = d.run_name
)
SELECT run_name, battery, arm, seed, eval_track,
       COUNT(*)                                             AS gens_used,
       100.0 * SUM(brake_ticks)    / NULLIF(SUM(alive_ticks), 0) AS brake_pct_alive,
       100.0 * SUM(overlap_ticks)  / NULLIF(SUM(alive_ticks), 0) AS overlap_pct_alive,
       100.0 * (SUM(brake_ticks) - SUM(overlap_ticks))
                                   / NULLIF(SUM(alive_ticks), 0) AS brake_alone_pct_alive,
       100.0 * SUM(near_wall_ticks)/ NULLIF(SUM(alive_ticks), 0) AS near_wall_pct_alive,
       100.0 * SUM(stationary_ticks)/NULLIF(SUM(alive_ticks), 0) AS stationary_pct_alive,
       SUM(impact_ticks) / NULLIF(SUM(distance_m) / 1000.0, 0)   AS impacts_per_km,
       SUM(collision_energy_j) / 1000.0
                         / NULLIF(SUM(distance_m) / 1000.0, 0)   AS collision_kj_per_km,
       SUM(speed_sum)    / NULLIF(SUM(alive_ticks), 0)           AS mean_speed_mps,
       SUM(throttle_sum) / NULLIF(SUM(alive_ticks), 0)           AS throttle_mean,
       SUM(distance_m)                                           AS distance_m
  FROM ranked WHERE from_end <= 5
 GROUP BY run_name;
"""

DRIVING_SUMS = ('alive_ticks', 'brake_ticks', 'overlap_ticks', 'impact_ticks',
                'near_wall_ticks', 'stationary_ticks', 'reverse_ticks', 'contact_ticks',
                'distance_m', 'collision_energy_j', 'throttle_sum', 'brake_sum',
                'speed_sum')


def connect(path: str = DEFAULT_PATH) -> sqlite3.Connection:
    """Open (creating if needed) the laboratory database with the schema applied."""
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    db.execute('PRAGMA journal_mode = WAL')
    # An existing database keeps its old table and view: `CREATE ... IF NOT EXISTS` adds no
    # column and replaces no view. Add missing columns, then rebuild the view from SCHEMA.
    existing = {row[1] for row in db.execute('PRAGMA table_info(run)')}
    if existing:
        for column, kind in RUN_COLUMNS_ADDED:
            if column not in existing:
                db.execute(f'ALTER TABLE run ADD COLUMN {column} {kind}')
        db.execute('DROP VIEW IF EXISTS v_last5')
    db.executescript(SCHEMA)
    return db


# ── ingestion ────────────────────────────────────────────────────────────────────────

def _sha256(path: str, limit: int = 1 << 20) -> str:
    """Checksum of the first megabyte plus the size -- enough to catch a replaced file
    without reading 18 MB of replay on every ingest."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read(limit))
    h.update(str(os.path.getsize(path)).encode())
    return h.hexdigest()


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def _driving_per_generation(path: str) -> dict[int, dict[str, float]]:
    """Sum every 64-tick window into its generation, keeping the coverage data that lets
    a caller reject a partial generation."""
    gens: dict[int, dict[str, float]] = {}
    last_tick: dict[int, dict[int, int]] = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            g = int(row['generation'])
            bucket = gens.setdefault(g, dict.fromkeys(DRIVING_SUMS, 0.0))
            for key in DRIVING_SUMS:
                bucket[key] += float(row[key])
            seen = last_tick.setdefault(g, {})
            being = int(row['being'])
            seen[being] = max(seen.get(being, 0), int(row['last_tick']))
    for g, seen in last_tick.items():
        gens[g]['beings'] = float(len(seen))
        gens[g]['min_last_tick'] = float(min(seen.values(), default=0))
    return gens


def ingest_run(db: sqlite3.Connection, out_dir: str, project: str = 'universe',
               battery: str | None = None) -> str | None:
    """Read one run directory into the database. Idempotent: re-ingesting replaces its
    rows and nothing else. Returns the run name, or None when the directory is not a run.

    `battery` overrides the battery derived from the name/args below. It exists for run
    directories that were never named `<battery>_<arm>_s<seed>` -- e.g.
    `Universe/artifacts/b1-s77-heldout-8200`, evaluation runs Astra produced by calling
    `gpu_evolve` directly, outside the runs root and its naming convention. Their
    `manifest.json` has a `command` list (raw argv), not the `args` dict that
    `universe_run.py` writes, so `args` is `{}` for them and `battery`/`arm`/`seed` fall
    through to NULL exactly like any other run whose name does not match -- this never
    crashes, it just leaves the caller to pass `--battery` if it wants them grouped.
    """
    manifest_path = os.path.join(out_dir, 'manifest.json')
    if not os.path.exists(manifest_path):
        return None
    with open(manifest_path) as f:
        manifest = json.load(f)
    name = manifest.get('id') or os.path.basename(out_dir.rstrip('/'))
    args = manifest.get('args', {}) or {}
    match = RUN_NAME.match(name)
    battery = battery or (match.group('battery') if match else None)
    arm = match.group('arm') if match else None
    seed = int(match.group('seed')) if match else args.get('seed')
    eval_track = int(match.group('track')) if match and match.group('track') else None

    config = None
    meta_path = os.path.join(out_dir, 'driving.meta.json')
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        # Only the fields that say WHICH CODE PATH ran; the rest is retina geometry.
        config = {k: meta[k] for k in (
            'slow_kinematics', 'wall_probes', 'motor_head', 'throttle_arbitration',
            'reverse_controller', 'contact_semantics', 'near_wall_semantics',
        ) if k in meta}

    population = sorted(f for f in os.listdir(out_dir) if f.startswith('population_gen'))
    gens_complete = len(population)
    requested = int(args.get('gens', 0) or 0)
    if requested > 0:
        status = 'finished' if gens_complete >= requested else 'running'
    elif manifest.get('simulation_exit') is not None:
        # A run launched outside the nmd wrapper (Astra's `Universe/artifacts/*`) carries a raw
        # argv and no `args`; the wrapper that wrote it records the exit code instead.
        status = 'finished' if int(manifest['simulation_exit']) == 0 else 'failed'
    else:
        status = 'running'

    db.execute('DELETE FROM run WHERE name = ?', (name,))
    db.execute(
        'INSERT INTO run (name, project, battery, arm, seed, out_dir, status, written,'
        ' lab_commit, script_sha256, gens_requested, gens_complete, ticks, beings, width,'
        ' tracks, wall_cost, impact_cost, command_json, args_json, config_json, ingested,'
        ' eval_track)'
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'), ?)",
        (name, project, battery, arm, seed, out_dir, status, manifest.get('written'),
         manifest.get('lab_commit'), manifest.get('script_sha256'),
         args.get('gens'), gens_complete, args.get('ticks'), args.get('beings'),
         args.get('width'), json.dumps(args.get('tracks')),
         args.get('wall-cost'), args.get('impact-cost'),
         json.dumps(manifest.get('command')), json.dumps(args), json.dumps(config),
         eval_track))

    for filename in population:
        gen = int(re.search(r'(\d+)', filename).group(1))
        with open(os.path.join(out_dir, filename)) as f:
            beings = json.load(f)
        rows = [(name, gen, b.get('being'), b.get('fitness'), b.get('progress_m'),
                 b.get('distance_m'), b.get('collision_energy_j'), b.get('impact_count'),
                 b.get('alive_ticks'), b.get('life_remaining_ticks'),
                 int(bool(b.get('life_exhausted'))), int(bool(b.get('low_progress'))),
                 b.get('fuel_remaining'), b.get('hole_hits'), b.get('x'), b.get('z'))
                for b in beings]
        db.executemany('INSERT INTO being_gen VALUES (' + ','.join('?' * 16) + ')', rows)
        progress = [float(b.get('progress_m') or 0.0) for b in beings]
        distance = [float(b.get('distance_m') or 0.0) for b in beings]
        alive = sum(int(b.get('alive_ticks') or 0) for b in beings)
        db.execute(
            'INSERT INTO generation VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (name, gen, len(beings), _median(progress),
             sum(progress) / max(len(progress), 1), max(progress, default=0.0),
             _median(distance), (sum(distance) / alive * 64.0) if alive else 0.0,
             sum(int(b.get('impact_count') or 0) for b in beings),
             sum(float(b.get('collision_energy_j') or 0.0) for b in beings),
             alive, sum(1 for b in beings if b.get('life_exhausted'))))

    driving_path = os.path.join(out_dir, 'driving.csv')
    if os.path.exists(driving_path):
        for gen, sums in _driving_per_generation(driving_path).items():
            columns = ('run_name', 'gen', *DRIVING_SUMS, 'beings', 'min_last_tick')
            db.execute(
                f"INSERT OR REPLACE INTO driving ({','.join(columns)})"
                f" VALUES ({','.join('?' * len(columns))})",
                (name, gen, *(sums[k] for k in DRIVING_SUMS),
                 int(sums.get('beings', 0)), int(sums.get('min_last_tick', 0))))

    for filename in sorted(os.listdir(out_dir)):
        path = os.path.join(out_dir, filename)
        if not os.path.isfile(path):
            continue
        if filename.endswith('.replay'):
            kind = 'replay'
        elif filename.endswith('.bin'):
            kind = 'genome'
        elif filename.endswith('.csv'):
            kind = 'csv'
        else:
            continue
        found = re.search(r'(\d{4})', filename)
        db.execute('INSERT OR REPLACE INTO artifact VALUES (?,?,?,?,?,?)',
                   (name, kind, int(found.group(1)) if found else None, path,
                    os.path.getsize(path), _sha256(path)))
    db.commit()
    return name


def ingest_tree(db: sqlite3.Connection, root: str, project: str = 'universe',
                battery: str | None = None) -> list[str]:
    """Ingest every run directory directly under `root`. Symlinks are skipped: two names
    for the same run would double-count it in any paired comparison. `battery` is passed
    through to `ingest_run` for trees whose directory names carry no battery of their
    own (see its docstring) -- e.g. `Universe/artifacts`."""
    done = []
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or os.path.islink(path) or entry.startswith('_'):
            continue
        name = ingest_run(db, path, project, battery=battery)
        if name:
            done.append(name)
    return done



# ── predictions ──────────────────────────────────────────────────────────────────────

# A ledger row is `| CODE | prose |`. The code is short and has no spaces: B1, B1c, F6v,
# U9v, 191v. Anything longer is a header or a wrapped line and is skipped.
LEDGER_ROW = re.compile(r'^\|\s*(?P<code>[A-Z0-9][A-Za-z0-9′″‴\'"-]{0,7})\s*\|\s*(?P<text>.+)$')
# This laboratory marks a VERDICT by suffixing the prediction code with `v` (F5v is the
# verdict on F3-F5, 191v on 191) and by the ✓/✗ glyphs. Those are conventions the project
# actually follows, so they can be read mechanically. Prose is NOT read: "refutada se X"
# is a refutation criterion every well-written bet contains, and "B1h estava errada" can
# be a conditional. Guessing a verdict from prose is worse than leaving it unset, because
# an agent will believe the column. `lab_db.py verdict <code> <status>` sets it by hand.
VERDICT_CODE = re.compile(r'v$')


def ingest_predictions(db: sqlite3.Connection, doc: str, project: str = 'universe',
                       battery: str | None = None) -> int:
    """Index a markdown prediction ledger. The document stays the written record; these
    rows only let an agent ask "which bets were refuted" without reading the whole table.

    The status is inferred from the prose and is therefore a HINT, not a verdict: the
    verdict lives in the document. Anything ambiguous is stored as 'registered'.
    """
    if not os.path.exists(doc):
        return 0
    inserted = 0
    with open(doc) as f:
        for line in f:
            match = LEDGER_ROW.match(line.rstrip('\n'))
            if not match:
                continue
            code = match.group('code').strip()
            text = match.group('text').rstrip('| \n')
            if not text or code.lower() in ('id', 'code', '---'):
                continue
            kind = 'verdict' if VERDICT_CODE.search(code) else 'prediction'
            status = None
            if '✗' in text:
                status = 'refuted'
            elif '✓' in text:
                status = 'confirmed'
            summary = re.sub(r'\*\*|`', '', text)
            summary = summary[:400] + ('…' if len(summary) > 400 else '')
            # A status already set by hand is never overwritten by a re-ingest.
            previous = db.execute(
                'SELECT status FROM prediction WHERE doc = ? AND code = ?',
                (doc, code)).fetchone()
            db.execute(
                'INSERT OR REPLACE INTO prediction (code, doc, project, battery, kind,'
                " registered, status, summary) VALUES (?,?,?,?,?,NULL,?,?)",
                (code, doc, project, battery or _battery_of(code), kind,
                 status or (previous['status'] if previous else None), summary))
            inserted += 1
    db.commit()
    return inserted


def _battery_of(code: str) -> str | None:
    """`B1c` belongs to battery `b1`; `F6v` to `f6`; a bare number to nothing."""
    match = re.match(r'^([A-Z]+\d+)', code)
    return match.group(1).lower() if match else None


def set_verdict(db: sqlite3.Connection, code: str, status: str,
                doc: str | None = None) -> int:
    """Record what a prediction turned out to be. This is the only writer of `status`."""
    if status not in ('confirmed', 'refuted', 'partial'):
        raise ValueError("status must be confirmed, refuted or partial")
    sql = 'UPDATE prediction SET status = ? WHERE code = ?'
    params: list[Any] = [status, code]
    if doc:
        sql += ' AND doc = ?'
        params.append(doc)
    changed = db.execute(sql, params).rowcount
    db.commit()
    return changed


def predictions(db: sqlite3.Connection, battery: str | None = None,
                status: str | None = None) -> list[sqlite3.Row]:
    sql = 'SELECT * FROM prediction WHERE 1=1'
    params: list[Any] = []
    for column, value in (('battery', battery), ('status', status)):
        if value is not None:
            sql += f' AND {column} = ?'
            params.append(value)
    return db.execute(sql + ' ORDER BY doc, code', params).fetchall()


# ── the reading API agents use ───────────────────────────────────────────────────────

def runs(db: sqlite3.Connection, battery: str | None = None, arm: str | None = None,
         status: str | None = None) -> list[sqlite3.Row]:
    sql = 'SELECT * FROM run WHERE 1=1'
    params: list[Any] = []
    for column, value in (('battery', battery), ('arm', arm), ('status', status)):
        if value is not None:
            sql += f' AND {column} = ?'
            params.append(value)
    return db.execute(sql + ' ORDER BY battery, arm, seed', params).fetchall()


def batteries(db: sqlite3.Connection) -> list[sqlite3.Row]:
    return db.execute(
        'SELECT battery, COUNT(*) AS runs, SUM(status = \'finished\') AS finished,'
        ' COUNT(DISTINCT arm) AS arms, COUNT(DISTINCT seed) AS seeds,'
        ' MIN(written) AS first_written, MAX(written) AS last_written'
        ' FROM run WHERE battery IS NOT NULL GROUP BY battery ORDER BY last_written DESC'
    ).fetchall()


def curve(db: sqlite3.Connection, run_name: str, metric: str = 'median_progress_m') -> list[tuple[int, float]]:
    if metric not in {c[1] for c in db.execute('PRAGMA table_info(generation)')}:
        raise ValueError(f'unknown generation metric: {metric}')
    return [(r[0], r[1]) for r in db.execute(
        f'SELECT gen, {metric} FROM generation WHERE run_name = ? ORDER BY gen', (run_name,))]


def paired(db: sqlite3.Connection, battery: str, left: str, right: str,
           metric: str = 'brake_pct_alive', include_running: bool = False,
           eval_track: int | None = None) -> dict[str, Any]:
    """The project's standard comparison: same seed both sides, effect size and how many
    seeds agree in DIRECTION -- never sigma on its own (memory `replicacao_vs_sigma`).

    Unfinished runs are excluded by default. `v_last5` means the last five generations
    that EXIST, so a run stopped at generation 6 would otherwise be compared against one
    that reached 30 -- the effective-generations confound that invalidated prediction 180
    in the taxi laboratory. `include_running=True` asks for an interim look and makes it
    the caller's responsibility to label the result as one.

    `eval_track=None` (default) compares TRAINING runs only. `eval_track=8200` compares the
    frozen-champion evaluations of both arms on that track. The two are never mixed: a
    training run and an evaluation of its champion share arm and seed, and before 16/09 a
    name like `b3_fixed_s31_t8005` did not even parse.
    """
    condition = '' if include_running else " AND ra.status = 'finished' AND rb.status = 'finished'"
    rows = db.execute(
        f'SELECT a.seed, a.{metric} AS l, b.{metric} AS r'
        ' FROM v_last5 a JOIN v_last5 b ON a.seed = b.seed AND a.battery = b.battery'
        # a training run pairs with a training run; an evaluation only with an evaluation
        # of the same seed ON THE SAME TRACK -- never 8005 against 8200
        ' AND a.eval_track IS b.eval_track'
        ' JOIN run ra ON ra.name = a.run_name JOIN run rb ON rb.name = b.run_name'
        f' WHERE a.battery = ? AND a.arm = ? AND b.arm = ? AND a.eval_track IS ?{condition}'
        ' ORDER BY a.seed',
        (battery, left, right, eval_track)).fetchall()
    diffs = [(row['seed'], row['l'] - row['r']) for row in rows]
    if not diffs:
        return {'metric': metric, 'n': 0, 'mean': None, 'per_seed': [], 'agree': 0}
    mean = sum(d for _, d in diffs) / len(diffs)
    agree = sum(1 for _, d in diffs if (d > 0) == (mean > 0))
    return {'metric': metric, 'left': left, 'right': right, 'n': len(diffs),
            'mean': mean, 'per_seed': diffs, 'agree': agree}


def drop_battery(db: sqlite3.Connection, battery: str) -> dict[str, Any]:
    """Delete a battery's ROWS and return the files it referenced, so the caller decides
    about the disk. Never deletes a file: that decision needs a human or an explicit
    sweeper, and a verdict already recorded is what makes replays disposable."""
    files = [dict(r) for r in db.execute(
        'SELECT a.kind, a.path, a.bytes FROM artifact a JOIN run r ON r.name = a.run_name'
        ' WHERE r.battery = ?', (battery,))]
    dirs = [r['out_dir'] for r in db.execute(
        'SELECT out_dir FROM run WHERE battery = ?', (battery,))]
    removed = db.execute('DELETE FROM run WHERE battery = ?', (battery,)).rowcount
    db.commit()
    # Report only what is actually on disk NOW. The artifact rows remember sizes from the last
    # ingest; a directory deleted since then must not be announced as remaining (16/09: `rm b2`
    # said "48 files, 0.32 GiB remain" about directories removed the night before).
    present = [f for f in files if os.path.exists(f['path'])]
    return {'battery': battery, 'runs_removed': removed, 'files': present,
            'dirs': [d for d in dirs if os.path.isdir(d)],
            'missing_files': len(files) - len(present),
            'bytes': sum(os.path.getsize(f['path']) for f in present)}


# ── annotations (lab-ui PRD §6: "scientific annotations go to lab.db, never to
# localStorage") ─────────────────────────────────────────────────────────────────────

def add_annotation(db: sqlite3.Connection, run: str, text: str, gen: int | None = None,
                    tick: int | None = None, author: str = '') -> int:
    """Record one note on a run, optionally scoped to a generation and/or a tick. Raises
    sqlite3.IntegrityError if `run` is not in the `run` table -- an annotation always
    points at something real."""
    cur = db.execute(
        'INSERT INTO annotation (run_name, gen, tick, author, text, created)'
        " VALUES (?,?,?,?,?, datetime('now'))",
        (run, gen, tick, author, text))
    db.commit()
    return cur.lastrowid


def annotations(db: sqlite3.Connection, run: str | None = None,
                 gen: int | None = None) -> list[sqlite3.Row]:
    sql = 'SELECT * FROM annotation WHERE 1=1'
    params: list[Any] = []
    for column, value in (('run_name', run), ('gen', gen)):
        if value is not None:
            sql += f' AND {column} = ?'
            params.append(value)
    return db.execute(sql + ' ORDER BY created', params).fetchall()


# ── trace index (lab-ui PRD §5: the trace-v1 contract itself is S0's job; this table
# only indexes the directories S2's producer writes) ─────────────────────────────────

def register_trace(db: sqlite3.Connection, run: str, gen: int, being: int, profile: str,
                    path: str, schema_version: int | None, manifest_sha256: str | None,
                    size_bytes: int | None) -> None:
    """Index one trace-v1 directory. Idempotent on (run, gen, being, profile): producing
    the same trace again (same manifest hash or not) replaces the row -- the row is a
    pointer, the manifest's own hashes are what say whether the bytes on disk are stale."""
    db.execute(
        'INSERT OR REPLACE INTO trace (run_name, gen, being, profile, schema_version, path,'
        " manifest_sha256, bytes, produced) VALUES (?,?,?,?,?,?,?,?, datetime('now'))",
        (run, gen, being, profile, schema_version, path, manifest_sha256, size_bytes))
    db.commit()


def traces(db: sqlite3.Connection, run: str | None = None) -> list[sqlite3.Row]:
    sql = 'SELECT * FROM trace WHERE 1=1'
    params: list[Any] = []
    if run is not None:
        sql += ' AND run_name = ?'
        params.append(run)
    return db.execute(sql + ' ORDER BY run_name, gen, being, profile', params).fetchall()


# ── queue mirror (lab-ui PRD §6 Queue panel: "mirrors `_nmd`") ───────────────────────

DEFAULT_SPOOL = '/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd'


def mirror_queue(db: sqlite3.Connection, spool: str = DEFAULT_SPOOL) -> int:
    """Snapshot the nmd spool (`neuromod-lab/scripts/nmd.py`) into `queue_mirror`. READ
    ONLY: this never writes into `spool`, only into the database. REPLACES the table on
    every call -- it mirrors what is on disk right now, it is not a history of what once
    passed through the queue.

    A request file lives in `pedidos/` from the moment it is written until nmd.py moves
    it to `feitos/` (done, success or failure) or `recusados/` (refused before it ever
    ran). While it is in `pedidos/`, `estado/<id>.json` says whether it is actually
    running (`fase: "rodando"`) or still waiting its turn -- that is the only distinction
    this function has to compute; the rest is which folder the file is in.
    """
    running_ids: set[str] = set()
    estado_dir = os.path.join(spool, 'estado')
    if os.path.isdir(estado_dir):
        for filename in os.listdir(estado_dir):
            if not filename.endswith('.json'):
                continue
            try:
                with open(os.path.join(estado_dir, filename)) as f:
                    estado = json.load(f)
            except (OSError, ValueError):
                continue
            if isinstance(estado, dict) and estado.get('fase') == 'rodando':
                running_ids.add(str(estado.get('id') or filename[:-len('.json')]))

    rows = []
    for folder, default_state in (('pedidos', 'pending'), ('feitos', 'done'),
                                   ('recusados', 'refused')):
        directory = os.path.join(spool, folder)
        if not os.path.isdir(directory):
            continue
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith('.json'):
                continue
            path = os.path.join(directory, filename)
            request_id = filename[:-len('.json')]
            script = out = args_json = None
            try:
                with open(path) as f:
                    payload = json.load(f)
                if isinstance(payload, dict):
                    request_id = str(payload.get('id') or request_id)
                    script = payload.get('script')
                    out = payload.get('out')
                    args_json = json.dumps(payload.get('args', {}))
            except (OSError, ValueError):
                pass  # a mirror shows less, it never refuses to reflect a broken file
            state = 'running' if folder == 'pedidos' and request_id in running_ids \
                else default_state
            rows.append((request_id, state, script, out, args_json, path))

    db.execute('DELETE FROM queue_mirror')
    db.executemany(
        'INSERT OR REPLACE INTO queue_mirror (id, state, script, out, args_json,'
        " file_path, seen) VALUES (?,?,?,?,?,?, datetime('now'))", rows)
    db.commit()
    return len(rows)


# ── audit (lab-ui PRD §7: "one audit line in lab.db" per write route) ────────────────

AUDIT_ACTIONS = ('launch', 'cancel', 'edit', 'verdict', 'annotation')


def audit(db: sqlite3.Connection, who: str, action: str, payload: Any,
          note: str = '') -> int:
    """Append one audit line. Stores the sha256 of `payload`, never the payload -- the
    trail proves WHAT was sent without becoming a second, growing copy of every
    experiment schema or annotation text that passes through the write routes."""
    if action not in AUDIT_ACTIONS:
        raise ValueError(f'action must be one of {AUDIT_ACTIONS}, got {action!r}')
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    cur = db.execute(
        'INSERT INTO audit ("when", who, action, payload_sha256, note)'
        " VALUES (datetime('now'), ?, ?, ?, ?)",
        (who, action, digest, note))
    db.commit()
    return cur.lastrowid


def audits(db: sqlite3.Connection, who: str | None = None,
           action: str | None = None) -> list[sqlite3.Row]:
    sql = 'SELECT * FROM audit WHERE 1=1'
    params: list[Any] = []
    for column, value in (('who', who), ('action', action)):
        if value is not None:
            sql += f' AND {column} = ?'
            params.append(value)
    return db.execute(sql + ' ORDER BY id', params).fetchall()


# ── command line ─────────────────────────────────────────────────────────────────────

def _print_table(rows: Iterable[sqlite3.Row]) -> None:
    rows = list(rows)
    if not rows:
        print('(no rows)')
        return
    headers = list(rows[0].keys())
    widths = [max(len(h), *(len(_fmt(r[h])) for r in rows)) for h in headers]
    print('  '.join(h.ljust(w) for h, w in zip(headers, widths)))
    print('  '.join('-' * w for w in widths))
    for r in rows:
        print('  '.join(_fmt(r[h]).ljust(w) for h, w in zip(headers, widths)))


def _fmt(value: Any) -> str:
    if value is None:
        return '-'
    if isinstance(value, float):
        return f'{value:.3f}'
    return str(value)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--db', default=DEFAULT_PATH)
    sub = ap.add_subparsers(dest='command', required=True)

    p = sub.add_parser('ingest', help='read run directories into the database')
    p.add_argument('root')
    p.add_argument('--project', default='universe')
    p.add_argument('--battery', help='override battery for runs whose name/args carry'
                   ' none, e.g. Universe/artifacts/* -> --battery b1eval')

    p = sub.add_parser('list', help='list batteries, or the runs of one')
    p.add_argument('--battery')

    p = sub.add_parser('compare', help='paired difference between two arms')
    p.add_argument('battery')
    p.add_argument('left')
    p.add_argument('right')
    p.add_argument('--metric', default='brake_pct_alive')
    p.add_argument('--include-running', action='store_true')
    p.add_argument('--eval-track', type=int, default=None,
                   help='compare champion evaluations on this track instead of training runs')

    p = sub.add_parser('predictions', help='index a markdown prediction ledger')
    p.add_argument('doc', nargs='+')
    p.add_argument('--project', default='universe')

    p = sub.add_parser('verdict', help='record what a prediction turned out to be')
    p.add_argument('code')
    p.add_argument('status', choices=['confirmed', 'refuted', 'partial'])
    p.add_argument('--doc')

    p = sub.add_parser('sql', help='run a read-only query')
    p.add_argument('query')

    p = sub.add_parser('rm', help='delete a battery\'s rows (files are listed, not deleted)')
    p.add_argument('battery')
    p.add_argument('--yes', action='store_true')

    a = ap.parse_args()
    db = connect(a.db)

    if a.command == 'ingest':
        names = ingest_tree(db, a.root, a.project, battery=a.battery)
        print(f'ingested {len(names)} run(s) into {a.db}')
        for n in names:
            print('   ', n)
    elif a.command == 'list':
        _print_table(runs(db, battery=a.battery) if a.battery else batteries(db))
    elif a.command == 'compare':
        result = paired(db, a.battery, a.left, a.right, a.metric, a.include_running, a.eval_track)
        if not result['n']:
            print('no paired seeds for those arms')
            return
        print(f"{result['metric']}: {a.left} - {a.right} = {result['mean']:+.3f}"
              f"  (n={result['n']}, same direction {result['agree']}/{result['n']})")
        for seed, diff in result['per_seed']:
            print(f'   s{seed:<5d} {diff:+10.3f}')
    elif a.command == 'predictions':
        for doc in a.doc:
            print(f'{ingest_predictions(db, doc, a.project):4d} rows from {doc}')
    elif a.command == 'verdict':
        print(f'{set_verdict(db, a.code, a.status, a.doc)} row(s) updated')
    elif a.command == 'sql':
        lowered = a.query.strip().lower()
        if not (lowered.startswith('select') or lowered.startswith('with')):
            sys.exit('only SELECT/WITH are accepted here; use the Python API to write')
        _print_table(db.execute(a.query).fetchall())
    elif a.command == 'rm':
        if not a.yes:
            sys.exit(f'this would delete the rows of battery {a.battery}; pass --yes')
        report = drop_battery(db, a.battery)
        print(f"removed {report['runs_removed']} run(s) from the database")
        if report['missing_files']:
            print(f"{report['missing_files']} referenced file(s) were already gone from disk")
        print(f"{len(report['files'])} file(s), {report['bytes'] / 2**30:.2f} GiB, remain on disk:")
        for d in report['dirs']:
            print('   ', d)


if __name__ == '__main__':
    main()
