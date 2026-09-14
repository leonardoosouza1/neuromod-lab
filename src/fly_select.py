"""Selection on the fly map, open loop against a Universe champion replay.

Each individual is a SELECTION, never a weight: which afferent cell type receives each
observation, which (plus, minus) efferent types are read as each command, and which
neurons stay (mask). Fitness = mean Pearson correlation between the read commands and
the champion's applied commands over a window of frames. Arms:

  bind          bindings only, full map                       (does choosing I/O suffice?)
  prune         bindings + neuron pruning (docs/16 operator)   (does selecting neurons add?)
  random-mask   bindings + fixed random masks at the density prune reaches (sparsity alone?)
  shuffled      'prune' on a map with shuffled targets         (does the fly's wiring matter?)

    python src/fly_select.py --replay <file> --arm prune --gens 20 --beings 32 --frames 3000 --out <dir>
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import RateBrain
from flybrain.io_map import Bindings, Groups
from flybrain.replay import being_frames, observation_matrix
from flybrain.selection import dense_mask, filter_edges, prune_step, shuffle_targets


def pearson(a, b):
    """a (T, B, k), b (T, k) -> (B, k)"""
    a = a - a.mean(0); b = b - b.mean(0)
    return (a * b[:, None, :]).sum(0) / (a.norm(dim=0) * b.norm(dim=0)[None, :] + 1e-9)


@torch.no_grad()
def evaluate(cm, bind, mask, obs_t, target_t, tau_steps, scale, act):
    B, T = bind.B, obs_t.shape[0]
    brain = RateBrain(cm, B, device='cuda', tau_steps=tau_steps, scale=scale, act=act)
    brain.set_neuron_mask(mask)
    cmd = torch.zeros((T, B, 3), device='cuda')
    for t in range(T):
        brain.step(bind.drive(obs_t[t].expand(B, -1)))
        cmd[t] = bind.read(brain.rates())
    rho = pearson(cmd, target_t).nan_to_num(0)
    return rho.mean(1), rho, float(brain.x.abs().max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--replay', required=True)
    ap.add_argument('--holdout-replay', default=None, help='second champion replay for generalization')
    ap.add_argument('--being', type=int, default=0)
    ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--holdout-offset', type=int, default=3000)
    ap.add_argument('--arm', choices=['bind', 'prune', 'random-mask', 'shuffled'], default='prune')
    ap.add_argument('--gens', type=int, default=20)
    ap.add_argument('--beings', type=int, default=32)
    ap.add_argument('--elite', type=float, default=0.25)
    ap.add_argument('--p-bind', type=float, default=0.15)
    ap.add_argument('--p-off', type=float, default=0.05)
    ap.add_argument('--p-on', type=float, default=0.015)
    ap.add_argument('--mask-density', type=float, default=0.35)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--tau-steps', type=float, default=4.0)
    ap.add_argument('--scale', type=float, default=1e-3)
    ap.add_argument('--gain', type=float, default=1.0)
    ap.add_argument('--act', default='tanh')
    ap.add_argument('--min-weight', type=int, default=1, help='drop edges with |synapses| below this (speed)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tag = f'fly_select_{a.arm}_s{a.seed}'
    logf = open(os.path.join(a.out, tag + '.log'), 'a')
    def log(s):
        print(s, flush=True); logf.write(s + '\n'); logf.flush()
    rng = np.random.default_rng(a.seed); torch.manual_seed(a.seed)
    cm = filter_edges(load_connectome(), a.min_weight)
    if a.arm == 'shuffled':
        cm = shuffle_targets(cm, a.seed)
    log(cm.summary())
    _, frames = being_frames(a.replay, a.being)
    obs, tgt = observation_matrix(frames), frames['final'].astype(np.float32)
    tr = slice(0, a.frames); ho = slice(a.holdout_offset, a.holdout_offset + a.frames)
    obs_tr, tgt_tr = torch.as_tensor(obs[tr], device='cuda'), torch.as_tensor(tgt[tr], device='cuda')
    obs_ho, tgt_ho = torch.as_tensor(obs[ho], device='cuda'), torch.as_tensor(tgt[ho], device='cuda')
    gi = Groups(cm, 'afferent', min_size=4); go = Groups(cm, 'efferent', min_size=2)
    log(f'{tag}: {a.frames} train frames, holdout frames {a.holdout_offset}.., afferent groups {gi.K}, efferent groups {go.K}, '
        f'target sd {tgt[tr].std(0).round(3).tolist()}')
    B = a.beings
    bind = Bindings.random(gi, go, B, obs.shape[1], 3, rng, gain=a.gain)
    if a.arm == 'random-mask':
        mask = (rng.random((B, cm.n)) < a.mask_density).astype(np.float32)
    else:
        mask = dense_mask(B, cm.n)
    protect = None
    hist = []
    t0 = time.time()
    for g in range(a.gens):
        m_t = torch.as_tensor(mask, device='cuda') if a.arm != 'bind' else None
        fit, rho, xmax = evaluate(cm, bind, m_t, obs_tr, tgt_tr, a.tau_steps, a.scale, a.act)
        f = fit.cpu().numpy(); order = np.argsort(f)[::-1]
        best = order[0]
        hist.append(dict(gen=g, best=float(f[best]), mean=float(f.mean()), rho_best=rho[best].cpu().numpy().round(3).tolist(),
                         density=float(mask[best].mean()), xmax=xmax, wall=time.time() - t0))
        log(f'  gen {g:3d}  best {f[best]:+.3f}  mean {f.mean():+.3f}  rho(thr,str,brk) {hist[-1]["rho_best"]}  '
            f'density {mask[best].mean():.3f}  max|x| {xmax:.2f}  {time.time() - t0:.0f}s')
        if g == a.gens - 1: break
        ne = max(2, int(B * a.elite)); elite = order[:ne]
        parents = elite[rng.integers(0, ne, B - ne)]
        child_b = bind.select(parents).mutate(rng, a.p_bind)
        child_m = mask[parents]
        if a.arm == 'prune':
            child_m = prune_step(child_m, rng, a.p_off, a.p_on, protect)
        bind = Bindings(gi, go, np.concatenate([bind.in_group.cpu().numpy()[elite], child_b.in_group.cpu().numpy()]),
                        np.concatenate([bind.out_pair.cpu().numpy()[elite], child_b.out_pair.cpu().numpy()]), a.gain)
        mask = np.concatenate([mask[elite], child_m])
    # ---- holdout: same champion, later window; optional second champion ------------------------
    m_t = torch.as_tensor(mask, device='cuda') if a.arm != 'bind' else None
    fit_ho, rho_ho, _ = evaluate(cm, bind, m_t, obs_ho, tgt_ho, a.tau_steps, a.scale, a.act)
    res = dict(args=vars(a), hist=hist, train_best=hist[-1]['best'],
               holdout_best_individual=float(fit_ho[best]), holdout_rho=rho_ho[best].cpu().numpy().round(3).tolist(),
               holdout_max=float(fit_ho.max()), density_best=float(mask[best].mean()),
               bindings_best=dict(inputs=[gi.names[i] for i in bind.in_group[best].cpu().numpy()],
                                  outputs=[[go.names[p], go.names[m]] for p, m in bind.out_pair[best].cpu().numpy()]))
    if a.holdout_replay:
        _, fr2 = being_frames(a.holdout_replay, a.being)
        o2, t2 = observation_matrix(fr2)[tr], fr2['final'].astype(np.float32)[tr]
        f2, r2, _ = evaluate(cm, bind, m_t, torch.as_tensor(o2, device='cuda'), torch.as_tensor(t2, device='cuda'), a.tau_steps, a.scale, a.act)
        res['other_champion_best_individual'] = float(f2[best]); res['other_champion_rho'] = r2[best].cpu().numpy().round(3).tolist()
    np.save(os.path.join(a.out, tag + '_mask_best.npy'), mask[best].astype(np.uint8))
    with open(os.path.join(a.out, tag + '.json'), 'w') as f:
        json.dump(res, f, indent=1)
    log(f'{tag} DONE train {res["train_best"]:+.3f} holdout {res["holdout_best_individual"]:+.3f} '
        f'{"other " + format(res.get("other_champion_best_individual", float("nan")), "+.3f") if a.holdout_replay else ""} '
        f'density {res["density_best"]:.3f}  inputs {res["bindings_best"]["inputs"]}  outputs {res["bindings_best"]["outputs"]}')


if __name__ == '__main__':
    main()
