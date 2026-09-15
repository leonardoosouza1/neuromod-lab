"""Paired analysis of the braking battery (Universe prediction B1/B1c).

Reads the per-being, per-window CSV written by `gpu_evolve --driving-diagnostics` for each
arm and seed, aggregates it by generation, and reports the declared primary ruler plus the
secondaries, paired by seed.

Primary ruler, declared before the battery ran: fraction of ALIVE ticks with brake > 0,
averaged over the last N generations. Dead beings are excluded by construction, because the
denominator is `alive_ticks` and the simulator pins a dead being at brake = 1.

    python src/analyze_brake_battery.py --runs-root /media/llm-data/universe-runs/neuromod-lab-taxi \
        --arms legacy fixed nocost --seeds 31 77 113 --last 5 --out <dir>
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict

SUMS = ('alive_ticks', 'brake_ticks', 'impact_ticks', 'near_wall_ticks', 'stationary_ticks',
        'reverse_ticks', 'distance_m', 'collision_energy_j', 'throttle_sum', 'brake_sum',
        'contact_events', 'speed_sum')


def per_generation(path: str) -> dict[int, dict[str, float]]:
    """Sum every window of every being into one row per generation."""
    gens: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    with open(path) as f:
        for row in csv.DictReader(f):
            g = int(row['generation'])
            for k in SUMS:
                gens[g][k] += float(row[k])
    return {g: dict(v) for g, v in gens.items()}


def metrics(agg: dict[str, float]) -> dict[str, float]:
    """The ruler and its secondaries, as ratios of sums — never a mean of ratios.

    The project has paid for that distinction: a per-frame mean of `omega_real/omega_needed`
    once read +1.14 where the aggregate projection read +0.045, and the sign of the
    conclusion changed with it.
    """
    alive = max(agg['alive_ticks'], 1.0)
    km = max(agg['distance_m'], 1.0) / 1000.0
    return {
        'brake_pct_alive': 100.0 * agg['brake_ticks'] / alive,
        'brake_mean_when_on': agg['brake_sum'] / max(agg['brake_ticks'], 1.0),
        'impacts_per_km': agg['impact_ticks'] / km,
        'collision_kj_per_km': agg['collision_energy_j'] / 1000.0 / km,
        'near_wall_pct_alive': 100.0 * agg['near_wall_ticks'] / alive,
        'stationary_pct_alive': 100.0 * agg['stationary_ticks'] / alive,
        'reverse_pct_alive': 100.0 * agg['reverse_ticks'] / alive,
        'throttle_mean': agg['throttle_sum'] / alive,
        'mean_speed_mps': agg['speed_sum'] / alive,
        'distance_m': agg['distance_m'],
    }


def tail_mean(gens: dict[int, dict[str, float]], last: int) -> tuple[dict[str, float], list[int]]:
    """Metrics of the last `last` generations, aggregated as sums before ratios."""
    keys = sorted(gens)[-last:]
    total = {k: sum(gens[g][k] for g in keys) for k in SUMS}
    return metrics(total), keys


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', default='/media/llm-data/universe-runs/neuromod-lab-taxi')
    ap.add_argument('--prefix', default='b1')
    ap.add_argument('--arms', nargs='+', default=['legacy', 'fixed', 'nocost'])
    ap.add_argument('--seeds', nargs='+', type=int, default=[31, 77, 113])
    ap.add_argument('--last', type=int, default=5)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    table: dict[str, dict[int, dict[str, float]]] = {}
    curves: dict[str, dict[int, dict[int, float]]] = {}
    missing = []
    for arm in a.arms:
        table[arm] = {}
        curves[arm] = {}
        for s in a.seeds:
            path = os.path.join(a.runs_root, f'{a.prefix}_{arm}_s{s}', 'driving.csv')
            if not os.path.exists(path):
                missing.append(path)
                continue
            gens = per_generation(path)
            if not gens:
                missing.append(path)
                continue
            m, used = tail_mean(gens, a.last)
            m['generations_used'] = float(len(used))
            m['last_generation'] = float(max(gens))
            table[arm][s] = m
            curves[arm][s] = {g: metrics(gens[g])['brake_pct_alive'] for g in sorted(gens)}
    if missing:
        print(f'[warn] {len(missing)} run(s) without data yet:')
        for p in missing[:6]:
            print('   ', p)

    order = ['brake_pct_alive', 'impacts_per_km', 'collision_kj_per_km', 'near_wall_pct_alive',
             'distance_m', 'mean_speed_mps', 'throttle_mean', 'stationary_pct_alive']
    print(f'\n=== mean of the last {a.last} generations, per arm and seed ===')
    head = f"{'metric':22s}" + ''.join(f'{arm[:9]:>11s}' for arm in a.arms for _ in a.seeds)
    print(f"{'':22s}" + ''.join(f'  s{s:<8d}' for _ in a.arms for s in a.seeds))
    print(head)
    for k in order:
        line = f'{k:22s}'
        for arm in a.arms:
            for s in a.seeds:
                v = table[arm].get(s, {}).get(k)
                line += f'{v:11.3f}' if v is not None else f"{'--':>11s}"
        print(line)

    print(f'\n=== paired differences (same seed), primary ruler first ===')
    base = a.arms[-1] if 'nocost' in a.arms else a.arms[0]
    for k in order:
        for arm in a.arms:
            if arm == base:
                continue
            diffs = [(table[arm][s][k] - table[base][s][k])
                     for s in a.seeds if s in table[arm] and s in table[base]]
            if not diffs:
                continue
            mean = sum(diffs) / len(diffs)
            agree = sum(1 for d in diffs if (d > 0) == (mean > 0))
            print(f'  {k:22s} {arm:>8s} - {base:<8s} = {mean:+10.3f}   '
                  f'per seed {[round(d, 3) for d in diffs]}   same direction {agree}/{len(diffs)}')
        if k == order[0]:
            print()

    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, 'brake_battery.json'), 'w') as f:
            json.dump({'args': vars(a), 'tail_mean': table, 'brake_curve': curves}, f, indent=1)
        print(f"\nwrote {os.path.join(a.out, 'brake_battery.json')}")


if __name__ == '__main__':
    main()
