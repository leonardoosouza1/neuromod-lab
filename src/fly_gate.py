"""Gate for the fly map: reproduce Shiu et al. 2024 — stimulate the 21 right-hemisphere
sugar-sensing GRNs and check that the proboscis motor neuron MN9 fires.

Same constants as the reference model, batched over trials on the GPU. If this
gate fails (MN9 silent, or the brain runs away), the map/signs/units are wrong
and nothing built on top of it can be trusted.

    python src/fly_gate.py --rate-hz 100 --trials 30 --t-run-ms 1000 --out <dir>
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import LifBrain, LifParams

SUGAR_R = [720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345,
           720575940617000768, 720575940630797113, 720575940632889389, 720575940621754367,
           720575940621502051, 720575940640649691, 720575940639332736, 720575940616885538,
           720575940639198653, 720575940620900446, 720575940617937543, 720575940632425919,
           720575940633143833, 720575940612670570, 720575940628853239, 720575940629176663,
           720575940611875570]
MN9 = 720575940660219265


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rate-hz', type=float, default=100.0)
    ap.add_argument('--trials', type=int, default=30)
    ap.add_argument('--t-run-ms', type=float, default=1000.0)
    ap.add_argument('--silence', type=int, nargs='*', default=[], help='root ids to silence (outgoing edges = 0)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed)

    t0 = time.time()
    cm = load_connectome()
    print(cm.summary(), flush=True)
    sugar = cm.index_of(SUGAR_R)
    mn9 = int(cm.index_of([MN9])[0])
    edge_scale = None
    if a.silence:
        sil = set(cm.index_of(a.silence).tolist())
        edge_scale = torch.as_tensor(~np.isin(cm.csr_by_pre()[1], list(sil)), dtype=torch.float32)  # placeholder, replaced below
        # silence = zero every edge whose PRE is silenced (rows of csr_by_pre)
        indptr = cm.csr_by_pre()[0]
        keep = np.ones(len(cm.pre), dtype=np.float32)
        for i in sil:
            keep[indptr[i]:indptr[i + 1]] = 0.0
        edge_scale = torch.as_tensor(keep)
    brain = LifBrain(cm, a.trials, LifParams(), edge_scale=edge_scale)
    brain.set_poisson(sugar, a.rate_hz)
    steps = int(round(a.t_run_ms / brain.p.dt))
    t1 = time.time()
    for k in range(steps):
        brain.step()
        if k % 2000 == 0:
            torch.cuda.synchronize()
            print(f'  step {k}/{steps}  active so far {(brain.spike_count > 0).any(0).sum().item()}  {time.time() - t1:.1f}s', flush=True)
    torch.cuda.synchronize()
    wall = time.time() - t1
    rates = brain.rates_hz().cpu().numpy()
    per_trial_mn9 = brain.spike_count[:, mn9].float().cpu().numpy() / (a.t_run_ms * 1e-3)
    active = int((rates > 0).sum())
    order = np.argsort(rates)[::-1][:25]
    top = [dict(root_id=int(cm.root_ids[i]), rate_hz=float(rates[i]), cell_type=str(cm.neurons.cell_type[i]),
                super_class=str(cm.neurons.super_class[i])) for i in order]
    res = dict(rate_hz=a.rate_hz, trials=a.trials, t_run_ms=a.t_run_ms, steps=steps, wall_s=wall,
               mn9_rate_hz=float(per_trial_mn9.mean()), mn9_rate_sd=float(per_trial_mn9.std()),
               mn9_trials_firing=int((per_trial_mn9 > 0).sum()), active_neurons=active,
               total_spikes=int(brain.spike_count.sum().item()), silenced=a.silence, top=top)
    with open(os.path.join(a.out, f'fly_gate_{int(a.rate_hz)}hz.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'top'}))
    for t in top[:12]:
        print(f"  {t['rate_hz']:7.1f} Hz  {t['super_class']:10s} {t['cell_type']}")
    print(f'GATE {"PASSED" if res["mn9_rate_hz"] > 0 and active < 5000 else "FAILED"}: MN9 {res["mn9_rate_hz"]:.1f} Hz, '
          f'{active} active neurons, {wall:.0f}s for {a.trials} trials x {a.t_run_ms:.0f} ms')


if __name__ == '__main__':
    main()
