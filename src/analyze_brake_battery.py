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
import itertools
import json
import os
from collections import defaultdict

SUMS = ('alive_ticks', 'brake_ticks', 'impact_ticks', 'near_wall_ticks', 'stationary_ticks',
        'reverse_ticks', 'distance_m', 'collision_energy_j', 'throttle_sum', 'brake_sum',
        'contact_ticks', 'contact_events', 'overlap_ticks', 'speed_sum')


def per_generation(path: str) -> dict[int, dict[str, float]]:
    """Sum every window and retain enough coverage data to reject partial generations."""
    gens: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    last_tick: dict[int, dict[int, int]] = defaultdict(dict)
    with open(path) as f:
        for row in csv.DictReader(f):
            g = int(row['generation'])
            being = int(row['being'])
            for k in SUMS:
                gens[g][k] += float(row[k])
            last_tick[g][being] = max(last_tick[g].get(being, 0), int(row['last_tick']))
    result = {g: dict(v) for g, v in gens.items()}
    for g, ticks in last_tick.items():
        result[g]['_being_count'] = float(len(ticks))
        result[g]['_min_last_tick'] = float(min(ticks.values(), default=0))
    return result


def complete_generations(
    gens: dict[int, dict[str, float]], expected_ticks: int, expected_beings: int
) -> dict[int, dict[str, float]]:
    """Return only generations whose every expected being reached the final tick."""
    return {
        g: values
        for g, values in gens.items()
        if int(values.get('_being_count', 0)) == expected_beings
        and int(values.get('_min_last_tick', 0)) >= expected_ticks
    }


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
        'overlap_pct_alive': 100.0 * agg['overlap_ticks'] / alive,
        # POST-HOC decomposition, added 15/09 after the interim read, and labelled as such:
        # `overlap_ticks` counts ticks with brake > 0.05 AND throttle > 0.1, i.e. both pedals
        # at once — the missing mutual exclusion flagged in the architecture audit. The
        # pre-registered ruler (`brake_pct_alive`) counts every braking tick, including those.
        # This one counts braking that is NOT fighting the throttle, which is the only kind
        # that decelerates. It is a decomposition of the declared ruler, not a replacement.
        'brake_alone_pct_alive': 100.0 * max(agg['brake_ticks'] - agg['overlap_ticks'], 0.0) / alive,
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
    ap.add_argument('--allow-partial', action='store_true',
                    help='analyze completed generations from runs that are still in progress')
    a = ap.parse_args()

    table: dict[str, dict[int, dict[str, float]]] = {}
    curves: dict[str, dict[int, dict[int, float]]] = {}
    missing = []
    incomplete = []
    for arm in a.arms:
        table[arm] = {}
        curves[arm] = {}
        for s in a.seeds:
            path = os.path.join(a.runs_root, f'{a.prefix}_{arm}_s{s}', 'driving.csv')
            manifest_path = os.path.join(os.path.dirname(path), 'manifest.json')
            if not os.path.exists(path):
                missing.append(path)
                continue
            if not os.path.exists(manifest_path):
                missing.append(manifest_path)
                continue
            with open(manifest_path) as f:
                manifest = json.load(f)
            run_args = manifest.get('args', {})
            expected_gens = int(run_args.get('gens', 0))
            expected_ticks = int(run_args.get('ticks', 0))
            expected_beings = int(run_args.get('beings', 0))
            if min(expected_gens, expected_ticks, expected_beings) <= 0:
                missing.append(f'{manifest_path} (missing gens/ticks/beings)')
                continue
            observed = per_generation(path)
            gens = complete_generations(observed, expected_ticks, expected_beings)
            if not gens:
                missing.append(path)
                continue
            if len(gens) != expected_gens:
                incomplete.append((path, len(gens), expected_gens))
                if not a.allow_partial:
                    continue
            if len(gens) < a.last:
                missing.append(f'{path} (only {len(gens)} complete generations)')
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
    if incomplete:
        label = 'warn' if a.allow_partial else 'error'
        print(f'[{label}] {len(incomplete)} incomplete run(s):')
        for p, got, expected in incomplete:
            print(f'    {p}: {got}/{expected} complete generations')
    if incomplete and not a.allow_partial:
        raise SystemExit('battery is incomplete; pass --allow-partial for an interim analysis')

    order = ['brake_pct_alive', 'brake_alone_pct_alive', 'brake_mean_when_on', 'overlap_pct_alive', 'impacts_per_km',
             'collision_kj_per_km', 'near_wall_pct_alive', 'distance_m', 'mean_speed_mps',
             'throttle_mean', 'stationary_pct_alive', 'reverse_pct_alive']
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
    requested_pairs = []
    if 'fixed' in a.arms and 'legacy' in a.arms:
        requested_pairs.append(('fixed', 'legacy'))
    if 'fixed' in a.arms and 'nocost' in a.arms:
        requested_pairs.append(('fixed', 'nocost'))
    for left, right in itertools.combinations(a.arms, 2):
        if (left, right) not in requested_pairs and (right, left) not in requested_pairs:
            requested_pairs.append((left, right))
    for k in order:
        for left, right in requested_pairs:
            diffs = [(table[left][s][k] - table[right][s][k])
                     for s in a.seeds if s in table[left] and s in table[right]]
            if not diffs:
                continue
            mean = sum(diffs) / len(diffs)
            agree = sum(1 for d in diffs if (d > 0) == (mean > 0))
            print(f'  {k:22s} {left:>8s} - {right:<8s} = {mean:+10.3f}   '
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
