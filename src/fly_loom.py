"""Does the connectome detect an EXPANDING object — the stimulus its looming circuit is for?

F5v (Universe/docs/PREDICOES-CEREBRO.md) showed the steering reflex cannot drive a car: a track
offers at most a few percent of left/right drive imbalance, and the readout needs a fully
one-sided stimulus to swing. This asks the complementary question in open loop, before touching
the simulated world: with a LOCALISED disc of motion cells driven and its radius growing, does
LPLC2 / DNp01 rise with the radius, and does that rise survive a degree-preserving shuffle?

    python src/fly_loom.py --out <dir> [--map real|shuffle_targets] [--az 30]
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import RateBrain
from flybrain.eye import motion_chart
from flybrain.selection import MAP_VARIANTS

READ = {'LPLC2': r'^LPLC2$', 'LC4': r'^LC4$', 'LC6': r'^LC6$', 'DNp01': r'^DNp01$',
        'DNp_all': r'^DNp', 'HS': r'^HS', 'VS': r'^VS', 'DN_all': r'^DN'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', choices=sorted(MAP_VARIANTS), default='real')
    ap.add_argument('--az', type=float, default=30.0, help='disc centre azimuth, degrees')
    ap.add_argument('--el', type=float, default=0.0)
    ap.add_argument('--radii', type=float, nargs='*', default=[5, 10, 15, 20, 25, 30, 40, 50, 60])
    ap.add_argument('--drive', type=float, default=1.0)
    ap.add_argument('--steps', type=int, default=40)
    ap.add_argument('--scale', type=float, default=1e-3)
    ap.add_argument('--tau', type=float, default=4.0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed)
    cm = MAP_VARIANTS[a.map](load_connectome(), a.seed)
    chart = motion_chart(cm, '/media/llm-data/datasets/flywire/neuron_annotations.tsv')
    idx = chart['index'].to_numpy()
    d_from = lambda az: np.hypot(chart['azimuth_deg'].to_numpy() - az, chart['elevation_deg'].to_numpy() - a.el)
    groups = {k: cm.neurons.index[cm.neurons['cell_type'].str.match(v)].to_numpy() for k, v in READ.items()}
    side = cm.neurons['side'].to_numpy()
    rows, t0 = [], time.time()
    for az in (a.az, -a.az):
        dist = d_from(az)
        for r in a.radii:
            driven = idx[dist <= r]
            if len(driven) == 0:
                continue
            brain = RateBrain(cm, 1, device='cuda', tau_steps=a.tau, scale=a.scale, act='tanh')
            u = torch.zeros((cm.n, 1), device='cuda')
            u[torch.as_tensor(driven, device='cuda', dtype=torch.long), 0] = a.drive
            for _ in range(a.steps):
                brain.step(u)
            torch.cuda.synchronize()
            act = brain.rates()[:, 0].abs().cpu().numpy()
            row = {'azimuth': az, 'radius_deg': r, 'cells_driven': int(len(driven))}
            for g, mem in groups.items():
                row[g] = float(act[mem].mean())
                rr = act[mem[side[mem] == 'right']].mean() if (side[mem] == 'right').any() else 0.0
                ll = act[mem[side[mem] == 'left']].mean() if (side[mem] == 'left').any() else 0.0
                row[g + '_asym'] = float((rr - ll) / (rr + ll + 1e-9))
            rows.append(row)
            print(f"  az {az:+5.0f} r {r:4.0f}deg cells {len(driven):5d}  " +
                  '  '.join(f'{g} {row[g]:.4f}' for g in ('LPLC2', 'DNp01', 'DN_all')), flush=True)
    with open(os.path.join(a.out, f'fly_loom_{a.map}_s{a.seed}.json'), 'w') as f:
        json.dump({'args': vars(a), 'rows': rows}, f, indent=1)
    # the two numbers the prediction asks for
    pos = [r for r in rows if r['azimuth'] > 0]
    for g in ('LPLC2', 'DNp01', 'DN_all'):
        lo, hi = pos[0][g], pos[-1][g]
        print(f'EXPANSION GAIN {g:8s} r={pos[0]["radius_deg"]:.0f}deg -> {pos[-1]["radius_deg"]:.0f}deg: '
              f'{lo:.4f} -> {hi:.4f}  = {hi / max(lo, 1e-9):.2f}x')
    mid = len(a.radii) // 2
    l = [r for r in rows if r['azimuth'] < 0][mid]
    rr = pos[mid]
    print(f'SIDE SWING at r={rr["radius_deg"]:.0f}deg: LPLC2 asym {l["LPLC2_asym"]:+.3f} (left) -> '
          f'{rr["LPLC2_asym"]:+.3f} (right) = {rr["LPLC2_asym"] - l["LPLC2_asym"]:+.3f}')
    print(f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
