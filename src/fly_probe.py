"""Probe: does the fly map TRANSMIT the champion's sensors to its descending neurons?

Open loop on a Universe replay (being 0 = elite of the generation): 24 recorded
observations per frame are bound to random afferent cell-type groups, the map runs
one rate step per frame, and we ask whether any efferent group tracks the
champion's intent (throttle / steer / brake). Same random bindings on the real map
and on shuffled controls. No weights are generated: bindings + map only.

    python src/fly_probe.py --replay <file.replay> --being 0 --frames 3000 --beings 32 --out <dir>
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import RateBrain
from flybrain.io_map import Bindings, Groups
from flybrain.replay import being_frames, observation_matrix
from flybrain.selection import MAP_VARIANTS


def run_variant(name, cm, obs, intent, B, seed, tau_steps, scale, act, gain, log):
    dev = 'cuda'
    rng = np.random.default_rng(seed)
    gi = Groups(cm, 'afferent', min_size=4, device=dev)
    go = Groups(cm, 'efferent', min_size=2, device=dev)
    bind = Bindings.random(gi, go, B, obs.shape[1], 3, rng, gain=gain)
    brain = RateBrain(cm, B, device=dev, tau_steps=tau_steps, scale=scale, act=act)
    T = obs.shape[0]
    obs_t = torch.as_tensor(obs, device=dev)
    eff = cm.where(flow='efferent')
    eff_t = torch.as_tensor(eff, device=dev)
    cmd = torch.zeros((T, B, 3), device=dev)
    eff_rates = torch.zeros((T, len(eff), B), device=dev)
    torch.cuda.synchronize(); t0 = time.time()
    for t in range(T):
        u = bind.drive(obs_t[t].expand(B, -1))
        brain.step(u)
        r = brain.rates()
        cmd[t] = bind.read(r)
        eff_rates[t] = r[eff_t]
        if t % 1000 == 0:
            log(f'  [{name}] frame {t}/{T}  max|x| {brain.x.abs().max().item():.2f}  {time.time() - t0:.1f}s')
    torch.cuda.synchronize(); wall = time.time() - t0
    # --- metrics ---------------------------------------------------------------------------
    it = torch.as_tensor(intent, device=dev)                                   # (T, 3)
    def corr(a, b):  # a (T, ...), b (T,) -> corr over T
        a = a - a.mean(0); b = b - b.mean(0)
        return (a * b.view(-1, *([1] * (a.dim() - 1)))).sum(0) / (a.norm(dim=0) * b.norm() + 1e-9)
    ev = eff_rates.var(0)                                                      # (n_eff, B)
    frac_eff_alive = (ev > 1e-8).float().mean(0)                               # (B,)
    best_eff_corr = torch.stack([corr(eff_rates, it[:, j]).abs().nan_to_num(0).max(0).values for j in range(3)], 1)  # (B, 3)
    cmd_corr = torch.stack([corr(cmd[:, :, j], it[:, j]).abs().nan_to_num(0) for j in range(3)], 1)                   # (B, 3)
    res = dict(variant=name, wall_s=wall, ms_per_step=1000 * wall / T, max_abs_x=float(brain.x.abs().max()),
               frac_efferent_alive=frac_eff_alive.cpu().numpy().round(4).tolist(),
               best_efferent_corr=best_eff_corr.cpu().numpy().round(3).tolist(),
               cmd_corr=cmd_corr.cpu().numpy().round(3).tolist())
    med = lambda v: float(np.median(np.array(v), 0).mean()) if np.ndim(v) == 2 else float(np.median(v))
    log(f'  [{name}] {res["ms_per_step"]:.1f} ms/step  efferent alive median {med(res["frac_efferent_alive"]):.3f}  '
        f'best efferent |corr| median (thr,str,brk) {np.median(best_eff_corr.cpu().numpy(), 0).round(3).tolist()}  '
        f'bound cmd |corr| median {np.median(cmd_corr.cpu().numpy(), 0).round(3).tolist()}')
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--replay', required=True)
    ap.add_argument('--being', type=int, default=0)
    ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--beings', type=int, default=32)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--tau-steps', type=float, default=4.0)
    ap.add_argument('--scale', type=float, default=1e-3)
    ap.add_argument('--gain', type=float, default=1.0)
    ap.add_argument('--act', default='tanh')
    ap.add_argument('--variants', nargs='*', default=['real', 'shuffle_targets', 'shuffle_signs'])
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    logf = open(os.path.join(a.out, f'fly_probe_s{a.seed}.log'), 'a')
    def log(s):
        print(s, flush=True); logf.write(s + '\n'); logf.flush()
    torch.manual_seed(a.seed)
    cm = load_connectome(); log(cm.summary())
    header, frames = being_frames(a.replay, a.being)
    frames = frames[:a.frames]
    obs = observation_matrix(frames)
    intent = frames['final'].astype(np.float32)      # GPU replays record raw intent as zeros; the applied command is the target
    log(f'replay {a.replay} being {a.being}: {len(frames)} frames, tick_rate {header["tick_rate"]}, '
        f'final-command sd (thr,str,brk) {intent.std(0).round(3).tolist()}, arc {float(frames["arc_prog"].max()):.0f} m')
    results = []
    for v in a.variants:
        cmv = MAP_VARIANTS[v](cm, a.seed)
        results.append(run_variant(v, cmv, obs, intent, a.beings, a.seed, a.tau_steps, a.scale, a.act, a.gain, log))
    with open(os.path.join(a.out, f'fly_probe_s{a.seed}.json'), 'w') as f:
        json.dump(dict(args=vars(a), intent_sd=intent.std(0).tolist(), results=results), f, indent=1)
    log('PROBE DONE')


if __name__ == '__main__':
    main()
