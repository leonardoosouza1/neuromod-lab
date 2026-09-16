"""Battery B7 -- perception horizon (`--retina-range`). Pre-registered in
Universe/docs/PREDICOES-CEREBRO.md, row `B7` (2026-09-16 18:25, before running).
This script only reads final-champion evaluations; it does not touch training logs.

Arms, identical to `b5_rot` except the flag (tracks 8005/8100/8150, 32 beings, 25
gens, 12 000 ticks, no cost, fixed path, `--same-start`, frozen binary
`gpu_evolve-f5d203b`): `range60` (R=60), `range100` (R=100), `rand100` (R=100 +
`--largada-aleatoria`). Runs are `b7_<arm>_s<seed>`. Controls reused from B5 (same
binary, seeds, deterministic simulator): `easy` = `b5_rot_s<seed>` (R=33.3), `rand`
= `b5_rand_s<seed>`. Seeds 31/77/113/137.

Evaluation: final champion, same R as training (inherited flag), 1 generation, 8
clones = 1 measurement (20 000 ticks), tracks 8005/8200/8250/8218, read from
`<run>_eval_t<track>/` -- progress via `analyze_b6.read_progress` (same file,
same reading logic); crash speed via this module's `crash_speed` (`driving.csv`).

Rulers (B6r/B6x), crossed iff progress_m > threshold: 8200 > 1460; 8250 > 610;
8218 14 m curve > 790; 8218 12 m curve > 1130. Crossings sum per arm = crossings
over the three held-out rulers 8200, 8250, 8218-14m, 4 seeds each (max 12).

Crash speed (bet c mechanism): in `driving.csv`, rows for being 0 in tick order;
the LAST consecutive pair (a, b) with speed_a - speed_b > 12 m/s and
impact_ticks_b > 0 is a crash into a wall; crash speed = speed_a. Per seed: median
over its held-out evals (8200, 8250, 8218) that have a crash. Per arm: median over
seeds that have one.

Bets (pre-registered, B7):
  (a) 8200: range100 crosses the ruler in >= 3/4 seeds -> confirmed; <= 2/4 -> refuted.
  (b) dose: sum(range100) > sum(range60) > sum(easy) -> confirmed;
      sum(range100) <= sum(easy) -> refuted; else inconclusive.
  (c) mechanism: easy_crash_median - range100_crash_median >= 5 m/s -> confirmed;
      < 2 m/s -> refuted; else inconclusive.
  (d) no-cost on the training track: range100's lap fraction on 8005 (progress_m /
      1639) >= easy's, in >= 2/4 seeds -> confirmed, else refuted.
  (e) additivity: sum(rand100) >= sum(range100) -> confirmed, else refuted.

Any missing eval -> that bet's status is `pending` -- expected while B7
training/eval is still running (2026-09-16: only the b5-reused `easy`/`rand`
controls and the b7_* training-run directories exist; no b7_*_eval_t* yet).

    python src/analyze_b7.py
"""
from __future__ import annotations

import csv
import json
import os

from analyze_b6 import BASE, SEEDS, TRACKS, LAP_M, CROSS_M, read_progress, count_true, fmt

CROSS_8218 = {'14m': 790.0, '12m': 1130.0}
HELD_OUT_TRACKS = (8200, 8250, 8218)
HELD_OUT_KEYS = ('crossed_8200', 'crossed_8250', 'crossed_8218_14m')

ARM_RUN = {
    'range60': lambda s: f'b7_range60_s{s}',
    'range100': lambda s: f'b7_range100_s{s}',
    'rand100': lambda s: f'b7_rand100_s{s}',
    'easy': lambda s: f'b5_rot_s{s}',
    'rand': lambda s: f'b5_rand_s{s}',
}
ARMS = tuple(ARM_RUN)


def crash_speed(run: str, track: int) -> float | None:
    """Champion evaluation `driving.csv`: rows for being 0, in tick order. Returns
    speed_a of the LAST consecutive pair (a, b) with speed_a - speed_b > 12 m/s and
    impact_ticks_b > 0 (a crash into a wall). None if the eval does not exist, has
    no rows for being 0, or has no such pair (no crash recorded)."""
    path = os.path.join(BASE, f'{run}_eval_t{track}', 'driving.csv')
    if not os.path.exists(path):
        return None
    with open(path, newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['being'] == '0']
    rows.sort(key=lambda r: int(r['first_tick']))
    last = None
    for a, b in zip(rows, rows[1:]):
        speed_a, speed_b = float(a['speed']), float(b['speed'])
        if speed_a - speed_b > 12.0 and float(b['impact_ticks']) > 0:
            last = speed_a
    return last


def median(values: list[float]) -> float | None:
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        return None
    mid = n // 2
    return vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2.0


def crash_eval_files_exist(arm: str) -> bool:
    """True iff `driving.csv` exists for every seed and every held-out track of `arm`."""
    return all(
        os.path.exists(os.path.join(BASE, f'{ARM_RUN[arm](s)}_eval_t{t}', 'driving.csv'))
        for s in SEEDS for t in HELD_OUT_TRACKS
    )


def progress_complete(rows: dict, arm: str, tracks) -> bool:
    """True iff progress_m is not None for `arm` at every track in `tracks`, all 4 seeds."""
    return all(rows[(arm, s)]['progress_m'][t] is not None for s in SEEDS for t in tracks)


def collect() -> dict:
    rows = {}
    for arm in ARMS:
        for seed in SEEDS:
            run = ARM_RUN[arm](seed)
            prog = {t: read_progress(run, t) for t in TRACKS}
            lap_frac = {t: (prog[t] / LAP_M[t] if prog[t] is not None else None) for t in TRACKS}
            cs_by_track = {t: crash_speed(run, t) for t in HELD_OUT_TRACKS}
            cs_avail = [v for v in cs_by_track.values() if v is not None]
            rows[(arm, seed)] = {
                'run': run,
                'progress_m': prog,
                'lap_fraction': lap_frac,
                'crossed_8200': (prog[8200] > CROSS_M[8200]) if prog[8200] is not None else None,
                'crossed_8250': (prog[8250] > CROSS_M[8250]) if prog[8250] is not None else None,
                'crossed_8218_14m': (prog[8218] > CROSS_8218['14m']) if prog[8218] is not None else None,
                'crossed_8218_12m': (prog[8218] > CROSS_8218['12m']) if prog[8218] is not None else None,
                'crash_speed_by_track': cs_by_track,
                'crash_speed_seed_median': median(cs_avail) if cs_avail else None,
            }
    return rows


def arm_crossings_sum(rows: dict, arm: str) -> tuple[int, int]:
    """(n_true, n_avail) of the 3 held-out rulers x 4 seeds for `arm`; max 12."""
    n_true = n_avail = 0
    for s in SEEDS:
        for key in HELD_OUT_KEYS:
            v = rows[(arm, s)][key]
            if v is None:
                continue
            n_avail += 1
            n_true += v
    return n_true, n_avail


def arm_crash_median(rows: dict, arm: str) -> float | None:
    vals = [rows[(arm, s)]['crash_speed_seed_median'] for s in SEEDS]
    avail = [v for v in vals if v is not None]
    return median(avail) if avail else None


def bet_a(rows: dict) -> dict:
    if not progress_complete(rows, 'range100', (8200,)):
        return {'bet': 'a', 'track': 8200, 'status': 'pending'}
    n_true, n_avail = count_true(rows, 'range100', 'crossed_8200')
    status = 'confirmed' if n_true >= 3 else 'refuted'
    return {'bet': 'a', 'track': 8200, 'status': status, 'range100_crossed': f'{n_true}/{n_avail}'}


def bet_b(rows: dict) -> dict:
    arms = ('range100', 'range60', 'easy')
    if not all(progress_complete(rows, a, HELD_OUT_TRACKS) for a in arms):
        return {'bet': 'b', 'status': 'pending'}
    sums = {a: arm_crossings_sum(rows, a)[0] for a in arms}
    if sums['range100'] > sums['range60'] > sums['easy']:
        status = 'confirmed'
    elif sums['range100'] <= sums['easy']:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'b', 'status': status,
            'range100_sum': f"{sums['range100']}/12", 'range60_sum': f"{sums['range60']}/12",
            'easy_sum': f"{sums['easy']}/12"}


def bet_c(rows: dict) -> dict:
    if not (crash_eval_files_exist('easy') and crash_eval_files_exist('range100')):
        return {'bet': 'c', 'status': 'pending'}
    easy_m = arm_crash_median(rows, 'easy')
    r100_m = arm_crash_median(rows, 'range100')
    if easy_m is None or r100_m is None:
        return {'bet': 'c', 'status': 'pending', 'note': 'no crash found in complete data'}
    diff = easy_m - r100_m
    if diff >= 5.0:
        status = 'confirmed'
    elif diff < 2.0:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'c', 'status': status, 'easy_crash_median_mps': round(easy_m, 2),
            'range100_crash_median_mps': round(r100_m, 2), 'diff_mps': round(diff, 2)}


def bet_d(rows: dict) -> dict:
    if not (progress_complete(rows, 'range100', (8005,)) and progress_complete(rows, 'easy', (8005,))):
        return {'bet': 'd', 'track': 8005, 'status': 'pending'}
    n_true = sum(
        rows[('range100', s)]['lap_fraction'][8005] >= rows[('easy', s)]['lap_fraction'][8005]
        for s in SEEDS
    )
    status = 'confirmed' if n_true >= 2 else 'refuted'
    return {'bet': 'd', 'track': 8005, 'status': status, 'range100_ge_easy': f'{n_true}/4'}


def bet_e(rows: dict) -> dict:
    if not all(progress_complete(rows, a, HELD_OUT_TRACKS) for a in ('rand100', 'range100')):
        return {'bet': 'e', 'status': 'pending'}
    sum_rand100, _ = arm_crossings_sum(rows, 'rand100')
    sum_range100, _ = arm_crossings_sum(rows, 'range100')
    status = 'confirmed' if sum_rand100 >= sum_range100 else 'refuted'
    return {'bet': 'e', 'status': status, 'rand100_sum': f'{sum_rand100}/12', 'range100_sum': f'{sum_range100}/12'}


def fmt_speed(v) -> str:
    return '    NA' if v is None else f'{v:6.1f}'


def main() -> None:
    rows = collect()

    print(f"{'run':16s}{'p8005':>7s}{'p8200':>7s}{'x8200':>6s}{'p8250':>7s}{'x8250':>6s}"
          f"{'p8218':>7s}{'x14m':>6s}{'crash':>7s}")
    for arm in ARMS:
        for seed in SEEDS:
            r = rows[(arm, seed)]
            p = r['progress_m']
            print(f"{r['run']:16s}{fmt(p[8005])}{fmt(p[8200])}{fmt(r['crossed_8200'])}"
                  f"{fmt(p[8250])}{fmt(r['crossed_8250'])}{fmt(p[8218])}"
                  f"{fmt(r['crossed_8218_14m'])}{fmt_speed(r['crash_speed_seed_median'])}")

    print('\n=== per-arm summary (crossings sum /12 over 8200+8250+8218-14m; crash median m/s) ===')
    for arm in ARMS:
        n_true, n_avail = arm_crossings_sum(rows, arm)
        cm = arm_crash_median(rows, arm)
        cm_s = f'{cm:.1f}' if cm is not None else 'NA'
        print(f'{arm:12s} crossings={n_true}/{n_avail} crash_median={cm_s}')

    bets = [bet_a(rows), bet_b(rows), bet_c(rows), bet_d(rows), bet_e(rows)]
    print('\n=== bets (pre-registered, B7) ===')
    for b in bets:
        extra = ', '.join(f'{k}={v}' for k, v in b.items() if k not in ('bet', 'status'))
        print(f"({b['bet']}) status={b['status']} | {extra}")

    out_dir = os.path.join(BASE, 'b7-analise')
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        'runs': {f'{a}_s{s}': v for (a, s), v in rows.items()},
        'bets': bets,
    }
    with open(os.path.join(out_dir, 'b7.json'), 'w') as f:
        json.dump(payload, f, indent=1)
    print(f'\nwrote {out_dir}/b7.json')


if __name__ == '__main__':
    main()
