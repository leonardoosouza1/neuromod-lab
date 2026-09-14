"""How much left/right drive IMBALANCE does the fly's wiring need to move the steering readout?

Predictions 191v/193v drove one side and left the other silent — an infinite imbalance. On a
track both eyes see mostly road, so both sides are driven near the same (high) level and the
question is the SLOPE of the readout around balance, not its value at the extremes. This walks
the ratio from fully one-sided to balanced and reports the asymmetry index of the readout groups.

    python src/fly_transfer.py --out <dir> [--model rate] [--base-drive 1.0]
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import RateBrain
from flybrain.eye import motion_chart

GROUPS = {'HS': r'^HS', 'VS': r'^VS', 'HS_VS': r'^(HS|VS)', 'LPLC2': r'^LPLC2$', 'DN_all': r'^DN'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-drive', type=float, default=1.0, help='drive on the brighter side')
    ap.add_argument('--steps', type=int, default=40)
    ap.add_argument('--scale', type=float, default=1e-3)
    ap.add_argument('--tau', type=float, default=4.0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed)
    cm = load_connectome()
    chart = motion_chart(cm, '/media/llm-data/datasets/flywire/neuron_annotations.tsv')
    idx, az = chart['index'].to_numpy(), chart['azimuth_deg'].to_numpy()
    left, right = idx[az < 0], idx[az > 0]
    side = cm.neurons['side'].to_numpy()
    groups = {k: cm.neurons.index[cm.neurons['cell_type'].str.match(v)].to_numpy() for k, v in GROUPS.items()}
    ratios = [0.0, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5, 2.0, 4.0]
    rows = []
    t0 = time.time()
    for r in ratios:                      # r = left drive / right drive
        brain = RateBrain(cm, 1, device='cuda', tau_steps=a.tau, scale=a.scale, act='tanh')
        u = torch.zeros((cm.n, 1), device='cuda')
        u[torch.as_tensor(right, device='cuda', dtype=torch.long), 0] = a.base_drive
        u[torch.as_tensor(left, device='cuda', dtype=torch.long), 0] = a.base_drive * r
        for _ in range(a.steps):
            brain.step(u)
        torch.cuda.synchronize()
        act = brain.rates()[:, 0].abs().cpu().numpy()
        row = {'left_over_right': r}
        for g, members in groups.items():
            rr = float(act[members[side[members] == 'right']].mean()) if (side[members] == 'right').any() else 0.0
            ll = float(act[members[side[members] == 'left']].mean()) if (side[members] == 'left').any() else 0.0
            row[g] = (rr - ll) / (rr + ll + 1e-9)
        rows.append(row)
        print(f"  left/right {r:5.2f}  " + '  '.join(f'{g} {row[g]:+.3f}' for g in GROUPS), flush=True)
    with open(os.path.join(a.out, f'fly_transfer_s{a.seed}.json'), 'w') as f:
        json.dump({'args': vars(a), 'rows': rows}, f, indent=1)
    # the number that decides whether this can steer a car: slope of the index around balance
    i0 = [i for i, x in enumerate(rows) if x['left_over_right'] == 0.9][0]
    i1 = [i for i, x in enumerate(rows) if x['left_over_right'] == 1.1][0]
    for g in GROUPS:
        d = rows[i1][g] - rows[i0][g]
        print(f'SLOPE {g:7s} index change for a 20 % drive imbalance: {d:+.4f}   '
              f'(full one-sided swing: {rows[-1][g] - rows[0][g]:+.3f})')
    print(f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
