"""Vision gate for the fly map: does a dark expanding disk on the photoreceptors drive the
looming detectors (LPLC2 / LC4 / LC6) and the giant-fiber descending neurons (DNp01…)?

Brightness is encoded as photoreceptor Poisson rate (R1-6 are histaminergic: light
INHIBITS L1/L2; a dark patch releases them). Conditions, same trials/duration:
  loom      background everywhere, a dark disk at (az +30°, el 0°) grows 3° -> 40° over 100–400 ms
  scramble  the same NUMBER of dark photoreceptors at each step, at random positions
  static    a dark disk of 40° from 100 ms on, no expansion
Reference LIF model (Shiu et al. 2024) as in fly_gate.py; retinotopy from flybrain.eye.

    python src/fly_gate_looming.py --trials 10 --t-run-ms 400 --bg-hz 40 --out <dir>
"""
import argparse, json, os, sys, time

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import LifBrain, LifParams
from flybrain.eye import photoreceptor_chart

READOUT = {'LPLC2': r'^LPLC2$', 'LC4': r'^LC4$', 'LC6': r'^LC6$', 'T4': r'^T4', 'T5': r'^T5',
           'HS_VS': r'^(HS|VS)', 'DNp01': r'^DNp01$', 'DNp02_09': r'^DNp0[2-9]$', 'DNp': r'^DNp'}


def disk_radius(t_ms, t0=100.0, t1=400.0, r0=3.0, r1=40.0):
    if t_ms < t0:
        return 0.0
    return r0 + (r1 - r0) * min(1.0, (t_ms - t0) / (t1 - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--trials', type=int, default=10)
    ap.add_argument('--t-run-ms', type=float, default=400.0)
    ap.add_argument('--bg-hz', type=float, default=40.0)
    ap.add_argument('--az', type=float, default=30.0)
    ap.add_argument('--el', type=float, default=0.0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    cm = load_connectome()
    chart = photoreceptor_chart(cm, '/media/llm-data/datasets/flywire/neuron_annotations.tsv')
    r_idx = chart['index'].to_numpy()
    dist = np.hypot(chart['azimuth_deg'].to_numpy() - a.az, chart['elevation_deg'].to_numpy() - a.el)
    order_random = rng.permutation(len(r_idx))
    groups = {k: cm.neurons.index[cm.neurons['cell_type'].str.match(v)].to_numpy() for k, v in READOUT.items()}
    side = cm.neurons['side'].to_numpy()
    results = {}
    for cond in ['loom', 'scramble', 'static']:
        brain = LifBrain(cm, a.trials, LifParams())
        steps = int(round(a.t_run_ms / brain.p.dt))
        t0 = time.time()
        cur = None
        for k in range(steps):
            t_ms = k * brain.p.dt
            if cond == 'loom':
                dark = dist <= disk_radius(t_ms)
            elif cond == 'static':
                dark = dist <= (40.0 if t_ms >= 100.0 else 0.0)
            else:
                n_dark = int((dist <= disk_radius(t_ms)).sum())
                dark = np.zeros(len(r_idx), bool); dark[order_random[:n_dark]] = True
            key = int(dark.sum())
            if key != cur:                                  # only re-upload the lit set when it changes
                brain.set_poisson(r_idx[~dark], a.bg_hz); cur = key
            brain.step()
        torch.cuda.synchronize()
        rates = brain.rates_hz().cpu().numpy()
        # rates in the response window 150..400 ms would need a windowed count; the run is short, so whole-run rates
        res = {}
        for name, idx in groups.items():
            for s in ('left', 'right', 'all'):
                sel = idx if s == 'all' else idx[side[idx] == s]
                if len(sel):
                    res[f'{name}_{s}'] = float(rates[sel].mean())
        res['active_neurons'] = int((rates > 0).sum()); res['wall_s'] = time.time() - t0
        res['dnp01_trials_firing'] = int((brain.spike_count[:, groups['DNp01']].sum(1) > 0).sum())
        results[cond] = res
        print(f"{cond:9s} LPLC2 R/L {res['LPLC2_right']:.1f}/{res['LPLC2_left']:.1f}  LC4 R/L {res['LC4_right']:.1f}/{res['LC4_left']:.1f}  "
              f"LC6 R {res['LC6_right']:.1f}  T4 R {res['T4_right']:.1f}  HS/VS R {res['HS_VS_right']:.1f}  DNp01 {res['DNp01_all']:.1f} Hz "
              f"({res['dnp01_trials_firing']}/{a.trials} trials)  active {res['active_neurons']}  {res['wall_s']:.0f}s", flush=True)
    with open(os.path.join(a.out, f'fly_gate_looming_s{a.seed}.json'), 'w') as f:
        json.dump(dict(args=vars(a), results=results), f, indent=1)
    lo, sc, st = results['loom'], results['scramble'], results['static']
    ratio_sc = (lo['LPLC2_right'] + lo['LC4_right']) / max(1e-6, sc['LPLC2_right'] + sc['LC4_right'])
    ratio_st = (lo['LPLC2_right'] + lo['LC4_right']) / max(1e-6, st['LPLC2_right'] + st['LC4_right'])
    print(f'GATE looming/scramble = {ratio_sc:.2f}  looming/static = {ratio_st:.2f}  (LPLC2+LC4, stimulated side)')


if __name__ == '__main__':
    main()
