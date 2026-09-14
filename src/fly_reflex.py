"""Does the fly's own wiring produce a STEERING command from lateral motion?

This is the payoff test of using a real connectome: not "evolve a brain on it" but "read
a reflex the animal already has". Motion detectors are driven on ONE side of the visual
field and we read the descending neurons that carry steering and escape (DNa02, DNa01,
DNp09, DNp01, HS, VS, and the whole DN population), measuring LEFT-RIGHT ASYMMETRY.

The asymmetry index of a group is  (right - left) / (right + left)  of mean firing rate,
so +1 means only the right side fires. A steering signal exists if driving the left visual
field produces a different asymmetry than driving the right one.

Arms (same stimulus size, same trials, same seed):
  left / right   T4+T5 cells whose chart azimuth is on that side
  bilateral      the same number of cells split evenly over both sides (control for count)
  scramble       the same number of T4+T5 cells drawn at random regardless of side
and, with --map, the whole thing on a degree-preserving shuffled map.

    python src/fly_reflex.py --hz 100 --trials 8 --t-run-ms 300 --out <dir>
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import LifBrain, LifParams
from flybrain.eye import motion_chart
from flybrain.selection import MAP_VARIANTS

READOUT = {'DNa02': r'^DNa02$', 'DNa01': r'^DNa01$', 'DNa_all': r'^DNa', 'DNp01': r'^DNp01$',
           'DNp09': r'^DNp09$', 'DNp_all': r'^DNp', 'DNg_all': r'^DNg', 'HS': r'^HS', 'VS': r'^VS',
           'LPLC2': r'^LPLC2$', 'DN_all': r'^DN'}


def asymmetry(rates, idx, side):
    """(right - left) / (right + left) over the mean rates of a group; None if the group is silent."""
    r = float(rates[idx[side[idx] == 'right']].mean()) if (side[idx] == 'right').any() else 0.0
    l = float(rates[idx[side[idx] == 'left']].mean()) if (side[idx] == 'left').any() else 0.0
    tot = r + l
    return (None if tot <= 1e-9 else (r - l) / tot), r, l


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hz', type=float, default=100.0)
    ap.add_argument('--trials', type=int, default=8)
    ap.add_argument('--t-run-ms', type=float, default=300.0)
    ap.add_argument('--n-cells', type=int, default=2000, help='motion cells driven per arm')
    ap.add_argument('--map', choices=sorted(MAP_VARIANTS), default='real')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    cm = MAP_VARIANTS[a.map](load_connectome(), a.seed)
    print(f'[map] {a.map} {cm.summary()}', flush=True)
    chart = motion_chart(cm, '/media/llm-data/datasets/flywire/neuron_annotations.tsv')
    idx_all = chart['index'].to_numpy()
    az = chart['azimuth_deg'].to_numpy()
    side_arr = cm.neurons['side'].to_numpy()
    groups = {k: cm.neurons.index[cm.neurons['cell_type'].str.match(v)].to_numpy() for k, v in READOUT.items()}
    left_pool, right_pool = idx_all[az < 0], idx_all[az > 0]
    k = min(a.n_cells, len(left_pool), len(right_pool))
    arms = {
        'left': rng.choice(left_pool, k, replace=False),
        'right': rng.choice(right_pool, k, replace=False),
        'bilateral': np.concatenate([rng.choice(left_pool, k // 2, replace=False), rng.choice(right_pool, k // 2, replace=False)]),
        'scramble': rng.choice(idx_all, k, replace=False),
    }
    out = {}
    for name, driven in arms.items():
        brain = LifBrain(cm, a.trials, LifParams())
        brain.set_poisson(driven, a.hz)
        steps = int(round(a.t_run_ms / brain.p.dt))
        t0 = time.time()
        for _ in range(steps):
            brain.step()
        torch.cuda.synchronize()
        rates = brain.rates_hz().cpu().numpy()
        res = {'driven': int(len(driven)), 'active': int((rates > 0).sum()), 'wall_s': time.time() - t0}
        for g, idx in groups.items():
            asy, r, l = asymmetry(rates, idx, side_arr)
            res[g] = {'asym': asy, 'right_hz': round(r, 3), 'left_hz': round(l, 3)}
        out[name] = res
        parts = ' '.join(f"{g} {res[g]['right_hz']:6.1f}/{res[g]['left_hz']:6.1f}" for g in ('DNa02', 'DNa_all', 'DNp01', 'HS', 'VS'))
        print(f"{name:10s} driven {len(driven):5d} active {res['active']:6d}  R/L: {parts}  {res['wall_s']:.0f}s", flush=True)
    with open(os.path.join(a.out, f'fly_reflex_{a.map}_s{a.seed}.json'), 'w') as f:
        json.dump({'args': vars(a), 'arms': out}, f, indent=1)
    print('\n--- asymmetry index (right-left)/(right+left), by driven side ---')
    print(f"{'group':10s} {'left drive':>11s} {'right drive':>12s} {'bilateral':>10s} {'scramble':>9s}   swing(L->R)")
    for g in READOUT:
        v = [out[a_]['g' if False else g]['asym'] for a_ in ('left', 'right', 'bilateral', 'scramble')]
        f = lambda x: '   silent' if x is None else f'{x:+8.3f}'
        swing = '   n/a' if (v[0] is None or v[1] is None) else f'{v[1] - v[0]:+7.3f}'
        print(f'{g:10s} {f(v[0])} {f(v[1])} {f(v[2])} {f(v[3])}  {swing}')


if __name__ == '__main__':
    main()
