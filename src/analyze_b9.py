"""Battery B9 -- world that scales (curriculum by domain). Pre-registered in
Universe/docs/PREDICOES-CEREBRO.md, row `B9` (2026-09-16 20:54, before running).
This script only reads final-champion evaluations and training logs; it does
not touch or modify analyze_b6.py / analyze_b7.py / analyze_b8.py.

Arms `fixed` (track 8005 only), `pool` (rotation [8150, 8100, 8005, 8107,
8206, 8281] by generation, no curriculum), `escala` (same pool, in difficulty
order, with `--switch-on-complete 1`). Runs are `b9_<arm>_s<seed>`. New seeds
331/347/359/367, paired by seed.

Evaluation: final champion, tracks 8005/8131/8174/8233, read from
`<run>_eval_t<track>/` via `analyze_b6.read_progress` (same file, same
reading logic). Crash speed via `analyze_b7.crash_speed` (`driving.csv`) over
the 3 new held-out tracks 8131/8174/8233 -- descriptive only.

Lap lengths (m): 8005 1639, 8131 2313, 8174 2102, 8233 2590.

Four crossing rulers per seed, crossed iff progress_m > threshold:
8131 > 1160; 8174 > 470; 8233 > 1070; 8233 > 1840 (max 4 x 4 seeds = 16 per
arm).

Manipulation gate: in `_nmd/log/b9_escala_s<seed>.log`, count lines
containing both `[curriculo]` and `->` (an actual promotion, not the
"pista continua" no-promotion line -- same distinction as B6's lesson).
Gate passes iff count >= 2 in >= 3 of 4 seeds; otherwise bet (b) is
`non-informative`. Per escala seed we also report the last track reached,
parsed from the last `pista A -> B` promotion (falls back to the logged
initial track if there is no promotion yet).

Bets (pre-registered, B9):
  (a) sum(pool) - sum(fixed) >= 2 AND pool > fixed strictly in >= 2/4 seeds
      -> confirmed. sum(pool) <= sum(fixed) -> refuted. Else inconclusive.
  (b) gate fails -> non-informative. Else: sum(escala) - sum(pool) >= 2 AND
      escala > pool strictly in >= 2/4 -> confirmed. sum(escala) <= sum(pool)
      -> refuted. Else inconclusive.
  (c) descriptive: laps on 8005 per arm/seed (progress_m // lap length) and
      crash-speed median per arm (analyze_b7's rule) over 8131/8174/8233.

Any missing eval or log -> pending, never a crash -- expected 2026-09-16: b9
training is running now, no b9_*_eval_t* directories and no `[curriculo]`
promotions exist yet.

    python src/analyze_b9.py
"""
from __future__ import annotations

import json
import os
import re

from analyze_b6 import BASE, read_progress, fmt
from analyze_b7 import crash_speed, median
from analyze_b8 import seed_crossing_count

SEEDS = (331, 347, 359, 367)
EVAL_TRACKS = (8005, 8131, 8174, 8233)
LAP_M = {8005: 1639.0, 8131: 2313.0, 8174: 2102.0, 8233: 2590.0}
RULERS = ((8131, 1160.0), (8174, 470.0), (8233, 1070.0), (8233, 1840.0))
HELD_OUT_TRACKS = (8131, 8174, 8233)  # fresh, never-used-in-decision tracks

ARM_RUN = {
    'fixed': lambda s: f'b9_fixed_s{s}',
    'pool': lambda s: f'b9_pool_s{s}',
    'escala': lambda s: f'b9_escala_s{s}',
}
ARMS = tuple(ARM_RUN)

PROMOTION_RE = re.compile(r'pista\s+(\S+)\s*→\s*(\S+)')
INITIAL_RE = re.compile(r'pista inicial seed=(\d+)')


def collect() -> dict:
    rows = {}
    for arm in ARMS:
        for seed in SEEDS:
            run = ARM_RUN[arm](seed)
            prog = {t: read_progress(run, t) for t in EVAL_TRACKS}
            crossings = [None if prog[t] is None else prog[t] > thr for t, thr in RULERS]
            cs_by_track = {t: crash_speed(run, t) for t in HELD_OUT_TRACKS}
            cs_avail = [v for v in cs_by_track.values() if v is not None]
            laps_8005 = None if prog[8005] is None else int(prog[8005] // LAP_M[8005])
            rows[(arm, seed)] = {
                'run': run,
                'progress_m': prog,
                'crossings': crossings,
                'laps_8005': laps_8005,
                'crash_speed_by_track': cs_by_track,
                'crash_speed_seed_median': median(cs_avail) if cs_avail else None,
            }
    return rows


def arm_crossings_sum(rows: dict, arm: str) -> tuple[int, int]:
    """(n_true, n_avail) of the 4 rulers x 4 seeds for `arm` (max 16)."""
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


def escala_log_info(seed: int) -> dict:
    """Parse `_nmd/log/b9_escala_s<seed>.log` for `[curriculo]` promotions (lines
    that also contain `->`; the no-promotion `[curriculo]` line never does).
    `status`='pending' if the log does not exist yet."""
    path = os.path.join(BASE, '_nmd', 'log', f'b9_escala_s{seed}.log')
    if not os.path.exists(path):
        return {'status': 'pending'}
    with open(path, encoding='utf-8', errors='replace') as f:
        text = f.read()
    promo_lines = [ln for ln in text.splitlines() if '[curriculo]' in ln and '→' in ln]
    last_track = None
    if promo_lines:
        m = PROMOTION_RE.search(promo_lines[-1])
        if m:
            last_track = m.group(2)
    if last_track is None:
        m0 = INITIAL_RE.search(text)
        last_track = m0.group(1) if m0 else None
    return {'status': 'ok', 'n_promotions': len(promo_lines), 'last_track': last_track}


def manipulation_gate() -> tuple[str, dict]:
    """('pass'|'fail'|'pending', per-seed log info)."""
    info = {s: escala_log_info(s) for s in SEEDS}
    if any(v['status'] == 'pending' for v in info.values()):
        return 'pending', info
    n_ok = sum(1 for s in SEEDS if info[s]['n_promotions'] >= 2)
    return ('pass' if n_ok >= 3 else 'fail'), info


def bet_a(rows: dict) -> dict:
    counts = {(a, s): seed_crossing_count(rows, a, s) for a in ('fixed', 'pool') for s in SEEDS}
    if any(v is None for v in counts.values()):
        return {'bet': 'a', 'status': 'pending'}
    sum_pool, _ = arm_crossings_sum(rows, 'pool')
    sum_fixed, _ = arm_crossings_sum(rows, 'fixed')
    strict_gt = sum(counts[('pool', s)] > counts[('fixed', s)] for s in SEEDS)
    if sum_pool - sum_fixed >= 2 and strict_gt >= 2:
        status = 'confirmed'
    elif sum_pool <= sum_fixed:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'a', 'status': status, 'pool_sum': f'{sum_pool}/16',
            'fixed_sum': f'{sum_fixed}/16', 'pool_gt_fixed_strict': f'{strict_gt}/4'}


def bet_b(rows: dict, gate: str) -> dict:
    if gate == 'pending':
        return {'bet': 'b', 'status': 'pending', 'gate': gate}
    if gate == 'fail':
        return {'bet': 'b', 'status': 'non-informative', 'gate': gate}
    counts = {(a, s): seed_crossing_count(rows, a, s) for a in ('pool', 'escala') for s in SEEDS}
    if any(v is None for v in counts.values()):
        return {'bet': 'b', 'status': 'pending', 'gate': gate}
    sum_escala, _ = arm_crossings_sum(rows, 'escala')
    sum_pool, _ = arm_crossings_sum(rows, 'pool')
    strict_gt = sum(counts[('escala', s)] > counts[('pool', s)] for s in SEEDS)
    if sum_escala - sum_pool >= 2 and strict_gt >= 2:
        status = 'confirmed'
    elif sum_escala <= sum_pool:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {'bet': 'b', 'status': status, 'gate': gate, 'escala_sum': f'{sum_escala}/16',
            'pool_sum': f'{sum_pool}/16', 'escala_gt_pool_strict': f'{strict_gt}/4'}


def bet_c(rows: dict) -> dict:
    """Descriptive only: 8005 laps per arm/seed and crash-speed median per arm
    over the 3 new held-out tracks."""
    out = {'bet': 'c', 'status': 'descriptive',
           'laps_8005': {a: {s: rows[(a, s)]['laps_8005'] for s in SEEDS} for a in ARMS},
           'crash_speed_median_by_arm': {a: arm_crash_median(rows, a) for a in ARMS}}
    return out


def main() -> None:
    rows = collect()
    gate, gate_info = manipulation_gate()

    print(f"{'run':16s}{'p8005':>7s}{'p8131':>7s}{'p8174':>7s}{'p8233':>7s}{'x4':>4s}{'crash':>7s}")
    for arm in ARMS:
        for seed in SEEDS:
            r = rows[(arm, seed)]
            p = r['progress_m']
            cnt = seed_crossing_count(rows, arm, seed)
            cnt_s = f'{cnt:4d}' if cnt is not None else '  NA'
            cs = r['crash_speed_seed_median']
            cs_s = f'{cs:7.1f}' if cs is not None else '     NA'
            print(f"{r['run']:16s}{fmt(p[8005])}{fmt(p[8131])}{fmt(p[8174])}{fmt(p[8233])}{cnt_s}{cs_s}")

    print('\n=== per-arm summary (crossings sum /16; crash median m/s over 8131/8174/8233) ===')
    for arm in ARMS:
        n_true, n_avail = arm_crossings_sum(rows, arm)
        cm = arm_crash_median(rows, arm)
        cm_s = f'{cm:.1f}' if cm is not None else 'NA'
        print(f'{arm:12s} crossings={n_true}/{n_avail} crash_median={cm_s}')

    print(f'\n=== manipulation gate: {gate} (>=2 promotions in >=3/4 escala seeds) ===')
    for s in SEEDS:
        info = gate_info[s]
        if info['status'] == 'pending':
            print(f's{s}: pending (log missing)')
        else:
            print(f"s{s}: promotions={info['n_promotions']} last_track={info['last_track']}")

    bets = [bet_a(rows), bet_b(rows, gate), bet_c(rows)]
    print('\n=== bets (pre-registered, B9) ===')
    for b in bets:
        extra = ', '.join(f'{k}={v}' for k, v in b.items() if k not in ('bet', 'status'))
        print(f"({b['bet']}) status={b['status']} | {extra}")

    out_dir = os.path.join(BASE, 'b9-analise')
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        'runs': {f'{a}_s{s}': v for (a, s), v in rows.items()},
        'manipulation_gate': {'status': gate, 'per_seed': gate_info},
        'bets': bets,
    }
    with open(os.path.join(out_dir, 'b9.json'), 'w') as f:
        json.dump(payload, f, indent=1)
    print(f'wrote {out_dir}/b9.json')


if __name__ == '__main__':
    main()
