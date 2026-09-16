"""Battery B3: the 24 B1 champions frozen on the training track and on a held-out one.

Pre-registered in `Universe/docs/PREDICOES-CEREBRO.md` (B3) BEFORE the runs. The unit of
analysis is the champion: each run holds 8 clones of one genome from the same start in a
deterministic simulator, so a run is ONE measurement and this script asserts that (all
beings report the same progress) rather than averaging over copies.

Bets, as registered:
  (a) on 8005, the 14 champions that drove in training (mean speed > 10 m/s over the last 5
      generations) complete >= 3 laps; the 10 collapsed ones complete < 1.
      Refuted if >= 3 of the 14 stay below 3 laps.
  (b) on 8200 the median laps of the 14 drivers is <= 1. Refuted if > 1.
  (c) the fixed control path generalises better: progress_8200(fixed) - progress_8200(legacy)
      > 0 in >= 4/6 seeds with the cost, and nocost - legacy_nocost likewise without it.
      Refuted if <= 3/6 in either.
  (d) on 8200, corr(brake, time-to-contact) <= -0.10 in >= 8 of the 14 drivers.
      Refuted if fewer.

    python src/analyze_generalization.py [--runs-root ...] [--db /media/llm-data/lab.db]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_db  # noqa: E402

ARMS = ('legacy', 'fixed', 'legacy_nocost', 'nocost')
SEEDS = (31, 77, 113, 137, 191, 233)
TRACKS = (8005, 8200)
DRIVER_SPEED_MPS = 10.0


def lap_length(run_dir: str) -> float | None:
    log = os.path.join(run_dir, 'run.log')
    if not os.path.exists(log):
        # the nmd daemon keeps the log in its spool
        log = os.path.join(os.path.dirname(run_dir), '_nmd', 'log', os.path.basename(run_dir) + '.log')
    if not os.path.exists(log):
        return None
    with open(log, errors='replace') as f:
        for line in f:
            m = re.search(r'volta=(\d+)m', line)
            if m:
                return float(m.group(1))
    return None


def champion_result(run_dir: str) -> dict | None:
    path = os.path.join(run_dir, 'population_gen0000.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        beings = json.load(f)
    progress = sorted({round(float(b.get('progress_m') or 0.0), 3) for b in beings})
    b0 = beings[0]
    return {
        'progress_m': float(b0.get('progress_m') or 0.0),
        'distinct_progress_values': len(progress),
        'alive_ticks': int(b0.get('alive_ticks') or 0),
        'impact_count': int(b0.get('impact_count') or 0),
        'collision_energy_j': float(b0.get('collision_energy_j') or 0.0),
        'life_exhausted': bool(b0.get('life_exhausted')),
    }


def brake_ttc(run_dir: str) -> dict:
    """corr(brake, wall_front/speed) over alive windows with a visible wall, being 0 only:
    the clones are identical so any being would do, and pooling them would inflate n 8x."""
    path = os.path.join(run_dir, 'driving.csv')
    if not os.path.exists(path):
        return {'corr': float('nan'), 'n': 0, 'visible_pct': float('nan')}
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            if int(r['being']) != 0 or float(r['alive_ticks']) <= 0:
                continue
            rows.append((float(r['brake']), float(r['wall_front']), float(r['speed'])))
    if not rows:
        return {'corr': float('nan'), 'n': 0, 'visible_pct': float('nan')}
    far = max(r[1] for r in rows)
    vis = [r for r in rows if r[1] < far - 1e-6 and r[2] > 1.0]
    xs = [b for b, _, _ in vis]
    ys = [w / s for _, w, s in vis]
    n = len(xs)
    corr = float('nan')
    if n >= 3:
        mx, my = sum(xs) / n, sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        if sxx > 0 and syy > 0:
            corr = sxy / math.sqrt(sxx * syy)
    return {'corr': corr, 'n': n, 'visible_pct': 100.0 * len(vis) / len(rows)}


def training_speed(db: sqlite3.Connection, arm: str, seed: int) -> float | None:
    row = db.execute(
        "SELECT mean_speed_mps FROM v_last5 WHERE battery='b1' AND arm=? AND seed=?",
        (arm, seed)).fetchone()
    return float(row[0]) if row else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', default='/media/llm-data/universe-runs/neuromod-lab-taxi')
    ap.add_argument('--db', default=lab_db.DEFAULT_PATH)
    a = ap.parse_args()
    db = lab_db.connect(a.db)

    table: dict[tuple[str, int, int], dict] = {}
    laps_m: dict[int, float] = {}
    warnings = []
    for arm in ARMS:
        for seed in SEEDS:
            for track in TRACKS:
                run_dir = os.path.join(a.runs_root, f'b3_{arm}_s{seed}_t{track}')
                res = champion_result(run_dir)
                if res is None:
                    warnings.append(f'missing {run_dir}')
                    continue
                if res['distinct_progress_values'] != 1:
                    warnings.append(f'{os.path.basename(run_dir)}: clones NOT identical '
                                    f'({res["distinct_progress_values"]} progress values)')
                if track not in laps_m:
                    lap = lap_length(run_dir)
                    if lap:
                        laps_m[track] = lap
                res.update(brake_ttc(run_dir))
                res['laps'] = res['progress_m'] / laps_m[track] if track in laps_m else float('nan')
                res['train_speed'] = training_speed(db, arm, seed)
                table[(arm, seed, track)] = res

    print(f"lap length: {laps_m}")
    for w in warnings:
        print('[warn]', w)

    print(f"\n{'champion':22s}{'train m/s':>10s}{'laps 8005':>11s}{'laps 8200':>11s}"
          f"{'imp 8200':>9s}{'kJ 8200':>9s}{'vis% 8200':>10s}{'corr(brk,TTC) 8200':>20s}")
    drivers = []
    for arm in ARMS:
        for seed in SEEDS:
            r5, r2 = table.get((arm, seed, 8005)), table.get((arm, seed, 8200))
            if not r5 or not r2:
                continue
            ts = r5['train_speed']
            is_driver = ts is not None and ts > DRIVER_SPEED_MPS
            if is_driver:
                drivers.append((arm, seed))
            print(f"{arm + '/s' + str(seed):22s}{(ts if ts is not None else float('nan')):10.1f}"
                  f"{r5['laps']:11.2f}{r2['laps']:11.2f}{r2['impact_count']:9d}"
                  f"{r2['collision_energy_j'] / 1000:9.0f}{r2['visible_pct']:10.1f}"
                  f"{r2['corr']:20.3f}{'   driver' if is_driver else '   collapsed'}")

    print(f"\n=== bets (pre-registered) — {len(drivers)} drivers by the training rule (> {DRIVER_SPEED_MPS} m/s)")
    # (a)
    below = [(a_, s) for a_, s in drivers if table[(a_, s, 8005)]['laps'] < 3.0]
    collapsed = [(a_, s) for a_ in ARMS for s in SEEDS if (a_, s) not in drivers and (a_, s, 8005) in table]
    coll_ge1 = [(a_, s) for a_, s in collapsed if table[(a_, s, 8005)]['laps'] >= 1.0]
    print(f"(a) drivers < 3 laps on 8005: {len(below)}/{len(drivers)} {below}  -> "
          f"{'REFUTED' if len(below) >= 3 else 'holds'};  collapsed >= 1 lap: {len(coll_ge1)}/{len(collapsed)} {coll_ge1}")
    # (b)
    laps2 = sorted(table[(a_, s, 8200)]['laps'] for a_, s in drivers)
    med = (laps2[len(laps2) // 2 - 1] + laps2[len(laps2) // 2]) / 2 if laps2 and len(laps2) % 2 == 0 else (laps2[len(laps2) // 2] if laps2 else float('nan'))
    print(f"(b) median laps on 8200 among drivers: {med:.3f}  -> {'holds' if med <= 1.0 else 'REFUTED'}")
    # (c)
    for left, right, label in (('fixed', 'legacy', 'with cost'), ('nocost', 'legacy_nocost', 'without cost')):
        diffs = []
        for s in SEEDS:
            l, r = table.get((left, s, 8200)), table.get((right, s, 8200))
            if l and r:
                diffs.append((s, l['progress_m'] - r['progress_m']))
        pos = sum(1 for _, d in diffs if d > 0)
        print(f"(c) {label}: progress_8200({left}) - ({right}) > 0 in {pos}/{len(diffs)} seeds "
              f"{[(s, round(d)) for s, d in diffs]}  -> {'holds' if pos >= 4 else 'REFUTED'}")
    # (d)
    coupled = [(a_, s) for a_, s in drivers if table[(a_, s, 8200)]['corr'] <= -0.10]
    print(f"(d) drivers with corr(brake,TTC) <= -0.10 on 8200: {len(coupled)}/{len(drivers)}  -> "
          f"{'holds' if len(coupled) >= 8 else 'REFUTED'}")

    out = os.path.join(a.runs_root, 'b3-analise')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'generalization.json'), 'w') as f:
        json.dump({'lap_length': laps_m, 'drivers': drivers,
                   'table': {f'{k[0]}_s{k[1]}_t{k[2]}': v for k, v in table.items()}}, f, indent=1)
    print(f"\nwrote {out}/generalization.json")


if __name__ == '__main__':
    main()
