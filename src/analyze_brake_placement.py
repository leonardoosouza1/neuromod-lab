"""Is the brake PLACED or SPRAYED? (Universe battery B1, follow-up analysis.)

The pre-registered ruler of B1 counts braking ticks. It cannot distinguish a being that
brakes before a wall from one that rides the pedal everywhere, and B1's interim read made
that distinction the whole question: clean braking rises by +6.5 to +18.2 points in every
arm, including the arm where hitting a wall costs nothing.

This script uses the instantaneous snapshot that `driving.csv` already carries at the end of
every 64-tick window -- `brake`, `speed`, `wall_front` sampled at the SAME instant, so no
window averaging is involved. It asks two things of each run:

  1. correlation between the brake command and the distance to the wall ahead (negative means
     placed: the nearer the wall, the harder the brake);
  2. the same quantity early (first 3 generations, effectively random) against late (last 3),
     which is what says whether selection PLACED the pedal or merely pressed it harder.

Dead beings are excluded: the simulator pins `throttle=0, brake=1, steer=0` on death, so a
window with no alive ticks is a corpse reporting full brake.

    python src/analyze_brake_placement.py --arms legacy fixed nocost --seeds 31 77 113
"""
from __future__ import annotations

import argparse
import csv
import math
import os

# Columns used, by name; the header is read rather than assumed.
NEEDED = ('generation', 'being', 'alive_ticks', 'brake', 'speed', 'wall_front', 'throttle')


def read_snapshots(path: str) -> dict[int, list[tuple[float, float, float, float]]]:
    """Per generation, the list of (brake, wall_front, speed, throttle) of alive windows."""
    out: dict[int, list[tuple[float, float, float, float]]] = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            if float(row['alive_ticks']) <= 0.0:
                continue
            g = int(row['generation'])
            out.setdefault(g, []).append((
                float(row['brake']), float(row['wall_front']),
                float(row['speed']), float(row['throttle']),
            ))
    return out


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 3:
        return float('nan')
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0.0 or syy <= 0.0:
        return float('nan')
    return sxy / math.sqrt(sxx * syy)


def summarise(rows: list[tuple[float, float, float, float]]) -> dict[str, float]:
    brake = [r[0] for r in rows]
    wall = [r[1] for r in rows]
    near = [r[0] for r in rows if r[1] < 10.0]
    far = [r[0] for r in rows if r[1] > 30.0]
    return {
        'n': float(len(rows)),
        'corr_brake_wall': pearson(brake, wall),
        'brake_near': sum(near) / len(near) if near else float('nan'),
        'brake_far': sum(far) / len(far) if far else float('nan'),
        'frac_near': len(near) / max(len(rows), 1),
        'brake_mean': sum(brake) / max(len(brake), 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs-root', default='/media/llm-data/universe-runs/neuromod-lab-taxi')
    ap.add_argument('--prefix', default='b1')
    ap.add_argument('--arms', nargs='+', default=['legacy', 'fixed', 'nocost'])
    ap.add_argument('--seeds', nargs='+', type=int, default=[31, 77, 113])
    ap.add_argument('--edge', type=int, default=3, help='generations taken at each end')
    a = ap.parse_args()

    print(f"{'run':18s}{'phase':7s}{'n':>8s}{'corr(brake,wall)':>18s}"
          f"{'brake<10m':>11s}{'brake>30m':>11s}{'near-far':>10s}{'brake_all':>11s}")
    for arm in a.arms:
        for s in a.seeds:
            path = os.path.join(a.runs_root, f'{a.prefix}_{arm}_s{s}', 'driving.csv')
            if not os.path.exists(path):
                continue
            snaps = read_snapshots(path)
            gens = sorted(snaps)
            if len(gens) < 2 * a.edge:
                continue
            phases = (('early', gens[:a.edge]), ('late', gens[-a.edge:]))
            for label, keys in phases:
                rows = [r for g in keys for r in snaps[g]]
                m = summarise(rows)
                delta = m['brake_near'] - m['brake_far']
                print(f'{arm}/s{s:<12d}'[:18].ljust(18) + f'{label:7s}{int(m["n"]):8d}'
                      f'{m["corr_brake_wall"]:18.3f}{m["brake_near"]:11.3f}'
                      f'{m["brake_far"]:11.3f}{delta:+10.3f}{m["brake_mean"]:11.3f}')


if __name__ == '__main__':
    main()
