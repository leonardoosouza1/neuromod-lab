"""Battery B6 (redesigned) -- tight-curve dose-response. Pre-registered in
Universe/docs/PREDICOES-CEREBRO.md, row `B6r` (2026-09-16 17:06, before running).
This script only reads final-champion evaluations; it does not touch training logs.

Arms, each changing training tracks against the B5 baseline (32 beings, 25 gens,
12 000 ticks, no cost, fixed path, `--same-start`, frozen binary `gpu_evolve-f5d203b`):
  tight11      = 8005 + 8107 (11 m curve at 580 m) + 8206 (11 m curve at 730 m)
  tight8       = 8005 + 8107 + 8281 (8 m curve at 930 m) -- differs from tight11 by one track
  tight11rand  = tight11 + `--largada-aleatoria` (random start; additivity check)
Runs are `b6_<arm>_s<seed>`. Reused from B5 (same binary, seeds, deterministic
simulator): `easy` = `b5_rot_s<seed>`, `rand` = `b5_rand_s<seed>`. Seeds 31/77/113/137.

Evaluation: final champion, 1 generation, 8 clones = 1 measurement (20 000 ticks),
tracks 8005 / 8200 / 8250 / 8218, read from `<run>_eval_t<track>/population_gen0000.json`
-- same reading logic as `analyze_b5.py: eval_laps` (progress_m of the identical
clones, warn if they are not identical, take the value as-is).

Lap lengths (m): 8005 1639, 8200 2377, 8250 2340, 8218 2322.
Crossing rulers, declared before the run (crossed iff progress_m > threshold):
  8200 > 1460 m ; 8250 > 610 m ; 8218 has two curves in series: 12 m at 1130 m,
  8 m at 2110 m (dose in two steps).

Bets (pre-registered, B6r):
  (a) 8200: tight11 AND tight8 cross in >= 3/4 seeds each. Refuted if either <= 2/4.
  (b) dose on 8218 (8 m curve): tight8 crosses in >= 3/4 and tight11 in <= 1/4.
      tight11 >= 3/4 refutes "curving generalizes regardless of trained radius"
      (the "faixa" hypothesis); tight8 <= 2/4 refutes "training on 8 m teaches 8 m".
      Anything else (data complete but neither refutation condition met) is inconclusive.
  (c) 8250: tight11 AND tight8 cross in >= 3/4 seeds each, same pattern as (a).
  (d) 8005: tight11 closes fewer laps (lower progress_m / lap_len) than easy, per
      seed, in >= 3/4 seeds. Refuted if <= 2/4.
  (e) additivity: tight11rand's SUM of lap fractions over the three held-out tracks
      (8200 + 8250 + 8218) >= tight11's sum, per seed, in >= 3/4 seeds.
      Refuted if <= 1/4. (count == 2 is inconclusive.)

A bet's decision needs all 4 seeds of every arm/track it depends on. If any of
those evaluations is missing on disk, that seed counts as missing and the bet's
status is `pending` -- expected while B6 training/eval is still running (2026-09-16:
only the b5-reused `easy`/`rand` arms and the b6_* training-run directories exist;
no b6_*_eval_t* directories yet).

    python src/analyze_b6.py
"""
from __future__ import annotations

import json
import os

BASE = '/media/llm-data/universe-runs/neuromod-lab-taxi'
SEEDS = (31, 77, 113, 137)
TRACKS = (8005, 8200, 8250, 8218)
LAP_M = {8005: 1639.0, 8200: 2377.0, 8250: 2340.0, 8218: 2322.0}
CROSS_M = {8200: 1460.0, 8250: 610.0}
CROSS_8218 = {'12m': 1130.0, '8m': 2110.0}

ARM_RUN = {
    'tight11': lambda s: f'b6_tight11_s{s}',
    'tight8': lambda s: f'b6_tight8_s{s}',
    'tight11rand': lambda s: f'b6_tight11rand_s{s}',
    'easy': lambda s: f'b5_rot_s{s}',
    'rand': lambda s: f'b5_rand_s{s}',
}
ARMS = tuple(ARM_RUN)


def read_progress(run: str, track: int) -> float | None:
    """Champion evaluation: 8 clones = 1 measurement. Same reading logic as
    analyze_b5.py: eval_laps -- progress_m from population_gen0000.json, warn if
    the 8 clones are not identical, take the value as-is. None if the eval does
    not exist on disk yet."""
    path = os.path.join(BASE, f'{run}_eval_t{track}', 'population_gen0000.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        beings = json.load(f)
    if not beings:
        return None
    values = {round(float(b.get('progress_m') or 0.0), 3) for b in beings}
    if len(values) != 1:
        print(f'[warn] {run}_eval_t{track}: clones NOT identical ({len(values)} values)')
    return float(beings[0].get('progress_m') or 0.0)


def collect() -> dict:
    rows = {}
    for arm in ARMS:
        for seed in SEEDS:
            run = ARM_RUN[arm](seed)
            prog = {t: read_progress(run, t) for t in TRACKS}
            lap_frac = {t: (prog[t] / LAP_M[t] if prog[t] is not None else None) for t in TRACKS}
            rows[(arm, seed)] = {
                'run': run,
                'progress_m': prog,
                'lap_fraction': lap_frac,
                'crossed_8200': (prog[8200] > CROSS_M[8200]) if prog[8200] is not None else None,
                'crossed_8250': (prog[8250] > CROSS_M[8250]) if prog[8250] is not None else None,
                'crossed_8218_12m': (prog[8218] > CROSS_8218['12m']) if prog[8218] is not None else None,
                'crossed_8218_8m': (prog[8218] > CROSS_8218['8m']) if prog[8218] is not None else None,
                # B6x (f): 14 m curve with a 300 m side opening at 720-750 m.
                'crossed_8218_14m': (prog[8218] > 790.0) if prog[8218] is not None else None,
            }
    return rows


def count_true(rows: dict, arm: str, key: str) -> tuple[int, int]:
    """(n_true, n_available) of rows[(arm, seed)][key] over the 4 seeds. A seed
    whose value is None (eval missing) does not count toward n_available."""
    vals = [rows[(arm, s)][key] for s in SEEDS]
    avail = [v for v in vals if v is not None]
    return sum(1 for v in avail if v), len(avail)


def two_arm_crossing_bet(rows: dict, bet: str, track: int, key: str,
                         easy_max: int | None = None) -> dict:
    """Shared shape of bets (a) and (c): tight11 AND tight8 cross in >= 3/4 seeds
    each; refuted if either is <= 2/4; pending if either arm has < 4 evals. Bet (c) also
    requires easy to cross in <= easy_max seeds (B6r: `easy` <= 2/4 on 8250)."""
    t11_true, t11_n = count_true(rows, 'tight11', key)
    t8_true, t8_n = count_true(rows, 'tight8', key)
    easy_true, easy_n = count_true(rows, 'easy', key)
    if t11_n < 4 or t8_n < 4:
        status = 'pending'
    elif easy_max is not None and easy_n < 4:
        status = 'pending'
    elif t11_true >= 3 and t8_true >= 3 and (easy_max is None or easy_true <= easy_max):
        status = 'confirmed'
    else:
        status = 'refuted'
    return {
        'bet': bet, 'track': track, 'status': status,
        'tight11_crossed': f'{t11_true}/{t11_n}',
        'tight8_crossed': f'{t8_true}/{t8_n}',
        'easy_crossed': f'{easy_true}/{easy_n}' if easy_n else 'missing',
    }


def bet_b_dose_8218(rows: dict) -> dict:
    t8_true, t8_n = count_true(rows, 'tight8', 'crossed_8218_8m')
    t11_true, t11_n = count_true(rows, 'tight11', 'crossed_8218_8m')
    if t8_n < 4 or t11_n < 4:
        status = 'pending'
    elif t8_true >= 3 and t11_true <= 1:
        status = 'confirmed'
    elif t11_true >= 3:
        status = 'refuted (tight11 also crosses the 8m curve -- curving generalizes, dose does not gate it)'
    elif t8_true <= 2:
        status = 'refuted (tight8 does not reliably cross the 8m curve it trained on)'
    else:
        status = 'inconclusive'
    return {
        'bet': 'b', 'track': 8218, 'curve': '8m', 'status': status,
        'tight8_crossed': f'{t8_true}/{t8_n}', 'tight11_crossed': f'{t11_true}/{t11_n}',
    }


def bet_d_laps_8005(rows: dict) -> dict:
    n_true = n_avail = 0
    missing = []
    for s in SEEDS:
        lt = rows[('tight11', s)]['lap_fraction'][8005]
        le = rows[('easy', s)]['lap_fraction'][8005]
        if lt is None or le is None:
            missing.append(s)
            continue
        n_avail += 1
        n_true += lt < le
    if n_avail < 4:
        status = 'pending'
    elif n_true >= 3:
        status = 'confirmed'
    else:
        status = 'refuted'
    return {
        'bet': 'd', 'track': 8005, 'status': status,
        'tight11_fewer_laps_than_easy': f'{n_true}/{n_avail}', 'missing_seeds': missing,
    }


def bet_e_additivity(rows: dict) -> dict:
    held_out = (8200, 8250, 8218)
    n_true = n_avail = 0
    missing = []
    for s in SEEDS:
        rand_frac = rows[('tight11rand', s)]['lap_fraction']
        base_frac = rows[('tight11', s)]['lap_fraction']
        parts = [rand_frac[t] for t in held_out] + [base_frac[t] for t in held_out]
        if any(v is None for v in parts):
            missing.append(s)
            continue
        n_avail += 1
        n_true += sum(rand_frac[t] for t in held_out) >= sum(base_frac[t] for t in held_out)
    if n_avail < 4:
        status = 'pending'
    elif n_true >= 3:
        status = 'confirmed'
    elif n_true <= 1:
        status = 'refuted'
    else:
        status = 'inconclusive'
    return {
        'bet': 'e', 'tracks': list(held_out), 'status': status,
        'tight11rand_ge_tight11': f'{n_true}/{n_avail}', 'missing_seeds': missing,
    }


# Side openings (free width > 30 m on one side, `pista_check --ate <lap>`), arc ranges in m.
OPENINGS = {
    8200: [(1390, 1420), (2200, 2200)],
    8250: [(550, 550), (1400, 1420), (1640, 1640)],
    8218: [(720, 740), (1060, 1090), (1990, 2020), (2090, 2110)],
}


def stops_at_openings(rows: dict) -> dict:
    """Per arm: (stops inside an opening window, stops) on held-out tracks. A stop is an
    evaluation that ended before one lap; the window is [start - 40 m, end + 30 m]."""
    out = {}
    for arm in ARMS:
        inside = total = 0
        for seed in SEEDS:
            for track, spans in OPENINGS.items():
                p = rows[(arm, seed)]['progress_m'][track]
                if p is None or p >= LAP_M[track]:
                    continue
                total += 1
                inside += any(a - 40 <= p <= b + 30 for a, b in spans)
        out[arm] = (inside, total)
    return out


def fmt(v) -> str:
    if v is None:
        return '    NA'
    if isinstance(v, bool):
        return '     Y' if v else '     N'
    return f'{v:6.0f}'


def main() -> None:
    rows = collect()

    print(f"{'run':16s}{'p8005':>7s}{'p8200':>7s}{'x8200':>6s}{'p8250':>7s}{'x8250':>6s}"
          f"{'p8218':>7s}{'x12m':>6s}{'x8m':>6s}")
    for arm in ARMS:
        for seed in SEEDS:
            r = rows[(arm, seed)]
            p = r['progress_m']
            print(f"{r['run']:16s}{fmt(p[8005])}{fmt(p[8200])}{fmt(r['crossed_8200'])}"
                  f"{fmt(p[8250])}{fmt(r['crossed_8250'])}{fmt(p[8218])}"
                  f"{fmt(r['crossed_8218_12m'])}{fmt(r['crossed_8218_8m'])}")

    bets = [
        two_arm_crossing_bet(rows, 'a', 8200, 'crossed_8200'),
        bet_b_dose_8218(rows),
        two_arm_crossing_bet(rows, 'c', 8250, 'crossed_8250', easy_max=2),
        bet_d_laps_8005(rows),
        bet_e_additivity(rows),
        two_arm_crossing_bet(rows, 'f', 8218, 'crossed_8218_14m'),
    ]
    stops = stops_at_openings(rows)
    print('\n=== stops at side openings (B6x descriptive; window -40/+30 m) ===')
    for arm, (inside, total) in stops.items():
        print(f'{arm:12s} {inside}/{total}')
    print('\n=== bets (pre-registered, B6r + B6x) ===')
    for b in bets:
        extra = ', '.join(f'{k}={v}' for k, v in b.items() if k not in ('bet', 'status'))
        print(f"({b['bet']}) status={b['status']} | {extra}")

    out_dir = os.path.join(BASE, 'b6-analise')
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        'runs': {f'{a}_s{s}': v for (a, s), v in rows.items()},
        'bets': bets,
    }
    with open(os.path.join(out_dir, 'b6.json'), 'w') as f:
        json.dump(payload, f, indent=1)
    print(f'\nwrote {out_dir}/b6.json')


if __name__ == '__main__':
    main()
