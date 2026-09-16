"""Battery B8 -- rand100 x rand33 confirmatory replication. Pre-registered in
Universe/docs/PREDICOES-CEREBRO.md, row `B8` (2026-09-16 19:39, before running).
This script only reads final-champion evaluations; it does not touch training logs.

Arms `rand100` (`--retina-range 100`) and `rand33` (default 33.3), otherwise
identical to `b5_rand` (track 8005, `--largada-aleatoria`, `--same-start`, 32
beings, 25 gens, 12 000 ticks, no cost, fixed path, frozen binary
`gpu_evolve-f5d203b`). Runs are `b8_<arm>_s<seed>`. New seeds 173/199/229/257/
283/311, paired by seed.

Evaluation: final champion, 1 generation, 8 clones = 1 measurement (20 000
ticks), tracks 8005/8227/8293/8107/8200, read from `<run>_eval_t<track>/` via
`analyze_b6.read_progress` (same file, same reading logic). Crash speed via
`analyze_b7.crash_speed` (`driving.csv`) over the 3 fresh held-out tracks
8227/8293/8107 -- descriptive only.

Lap lengths (m): 8005 1639, 8227 2309, 8293 2240, 8107 2221, 8200 2377.

Five crossing rulers per seed, crossed iff progress_m > threshold: 8227 > 250
and > 1280; 8293 > 760 and > 1690; 8107 > 640 (max 5 x 6 seeds = 30 per arm).
Descriptive only: 8200 (hairpin/"grampo") > 1460.

Bets (pre-registered, B8):
  (a) sum over seeds of crossings: rand100 > rand33 AND per-seed paired count
      rand100 >= rand33 in >= 4/6 seeds -> confirmed.
      sum(rand100) <= sum(rand33) -> refuted. Else inconclusive.
  (b) 8005 progress, paired rand100 > rand33: >= 4/6 -> confirmed;
      <= 2/6 -> refuted; 3/6 -> inconclusive.
  (c) descriptive, not a bet: 8200 hairpin crossings per arm.

Any missing eval -> pending, never a crash -- expected 2026-09-16: b8 training
is running now, no b8_*_eval_t* directories exist yet.

    python src/analyze_b8.py
"""
from __future__ import annotations

import json
import os

from analyze_b6 import BASE, read_progress, fmt
from analyze_b7 import crash_speed, median

SEEDS = (173, 199, 229, 257, 283, 311)
TRACKS = (8005, 8227, 8293, 8107, 8200)
CROSS_8200 = 1460.0
RULERS = ((8227, 250.0), (8227, 1280.0), (8293, 760.0), (8293, 1690.0), (8107, 640.0))
HELD_OUT_TRACKS = (8227, 8293, 8107)  # fresh, out-of-train tracks for crash speed

ARM_RUN = {
    'rand100': lambda s: f'b8_rand100_s{s}',
    'rand33': lambda s: f'b8_rand33_s{s}',
}
ARMS = tuple(ARM_RUN)


def collect() -> dict:
    rows = {}
    for arm in ARMS:
        for seed in SEEDS:
            run = ARM_RUN[arm](seed)
            prog = {t: read_progress(run, t) for t in TRACKS}
            crossings = [None if prog[t] is None else prog[t] > thr for t, thr in RULERS]
            cs_by_track = {t: crash_speed(run, t) for t in HELD_OUT_TRACKS}
            cs_avail = [v for v in cs_by_track.values() if v is not None]
            rows[(arm, seed)] = {
                'run': run,
                'progress_m': prog,
                'crossings': crossings,
                'crossed_8200': (prog[8200] > CROSS_8200) if prog[8200] is not None else None,
                'crash_speed_by_track': cs_by_track,
                'crash_speed_seed_median': median(cs_avail) if cs_avail else None,
            }
    return rows


def seed_crossing_count(rows: dict, arm: str, seed: int) -> int | None:
    """Count of True among the 5 rulers for one seed; None if any is missing."""
    vals = rows[(arm, seed)]['crossings']
    return None if any(v is None for v in vals) else sum(vals)


def arm_crossings_sum(rows: dict, arm: str) -> tuple[int, int]:
    """(n_true, n_avail) of the 5 rulers x 6 seeds for `arm` (max 30)."""
    n_true = n_avail = 0
    for s in SEEDS:
        for v in rows[(arm, s)]['crossings']:
            if v is None:
                continue
            n_avail += 1
            n_true += v
    return n_true, n_avail


def arm_crash_median(rows: dict, arm: str) -> float | None:
    avail = [rows[(arm, s)]['crash_speed_seed_median'] for s in SEEDS
             if rows[(arm, s)]['crash_speed_seed_median'] is not None]
    return median(avail) if avail else None


def bet_a(rows: dict) -> dict:
    counts = {(a, s): seed_crossing_count(rows, a, s) for a in ARMS for s in SEEDS}
    if any(v is None for v in counts.values()):
        return {'bet': 'a', 'status': 'pending'}
    sum_r100, _ = arm_crossings_sum(rows, 'rand100')
    sum_r33, _ = arm_crossings_sum(rows, 'rand33')
    paired_ge = sum(counts[('rand100', s)] >= counts[('rand33', s)] for s in SEEDS)
    if sum_r100 > sum_r33 and paired_ge >= 4:
        status = 'confirmed'
    elif sum_r100 <= sum_r33:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'a', 'status': status, 'rand100_sum': f'{sum_r100}/30',
            'rand33_sum': f'{sum_r33}/30', 'paired_rand100_ge_rand33': f'{paired_ge}/6'}


def bet_b(rows: dict) -> dict:
    if any(rows[(a, s)]['progress_m'][8005] is None for a in ARMS for s in SEEDS):
        return {'bet': 'b', 'track': 8005, 'status': 'pending'}
    n_true = sum(rows[('rand100', s)]['progress_m'][8005] > rows[('rand33', s)]['progress_m'][8005]
                 for s in SEEDS)
    if n_true >= 4:
        status = 'confirmed'
    elif n_true <= 2:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'b', 'track': 8005, 'status': status, 'rand100_gt_rand33': f'{n_true}/6'}


def bet_c(rows: dict) -> dict:
    """Descriptive only, not a pre-registered bet: 8200 hairpin crossings per arm."""
    out = {'bet': 'c', 'status': 'descriptive'}
    for arm in ARMS:
        avail = [rows[(arm, s)]['crossed_8200'] for s in SEEDS if rows[(arm, s)]['crossed_8200'] is not None]
        out[f'{arm}_crossed_8200'] = f'{sum(avail)}/{len(avail)}' if avail else 'pending'
    return out


def main() -> None:
    rows = collect()

    print(f"{'run':16s}{'p8005':>7s}{'p8227':>7s}{'p8293':>7s}{'p8107':>7s}{'p8200':>7s}{'x5':>4s}{'crash':>7s}")
    for arm in ARMS:
        for seed in SEEDS:
            r = rows[(arm, seed)]
            p = r['progress_m']
            cnt = seed_crossing_count(rows, arm, seed)
            cnt_s = f'{cnt:4d}' if cnt is not None else '  NA'
            cs = r['crash_speed_seed_median']
            cs_s = f'{cs:7.1f}' if cs is not None else '     NA'
            print(f"{r['run']:16s}{fmt(p[8005])}{fmt(p[8227])}{fmt(p[8293])}{fmt(p[8107])}{fmt(p[8200])}{cnt_s}{cs_s}")

    print('\n=== per-arm summary (crossings sum /30; crash median m/s over 8227/8293/8107) ===')
    for arm in ARMS:
        n_true, n_avail = arm_crossings_sum(rows, arm)
        cm = arm_crash_median(rows, arm)
        cm_s = f'{cm:.1f}' if cm is not None else 'NA'
        print(f'{arm:12s} crossings={n_true}/{n_avail} crash_median={cm_s}')

    bets = [bet_a(rows), bet_b(rows), bet_c(rows)]
    print('\n=== bets (pre-registered, B8) ===')
    for b in bets:
        extra = ', '.join(f'{k}={v}' for k, v in b.items() if k not in ('bet', 'status'))
        print(f"({b['bet']}) status={b['status']} | {extra}")

    out_dir = os.path.join(BASE, 'b8-analise')
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        'runs': {f'{a}_s{s}': v for (a, s), v in rows.items()},
        'bets': bets,
    }
    with open(os.path.join(out_dir, 'b8.json'), 'w') as f:
        json.dump(payload, f, indent=1)
    print(f'\nwrote {out_dir}/b8.json')


if __name__ == '__main__':
    main()
