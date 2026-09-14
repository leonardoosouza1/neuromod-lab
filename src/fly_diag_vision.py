"""Diagnostic of the fly visual pathway on the FlyWire v783 map (LIF, Shiu et al. 2024).

The sugar gate (`fly_gate.py`, prediction 186v) passes: 20 sugar GRNs at 100 Hz -> MN9 at
72.4 Hz, 420 active neurons. The looming gate (`fly_gate_looming.py`, prediction 189) does
not: ~7900 R1-6 photoreceptors at 40 Hz activate 9428 neurons, yet LPLC2 / LC4 / LC6 / T4 /
T5 / HS / VS / DNp01 all read 0.0 Hz. This script finds out WHERE the activity dies and WHY.

What it reports
  * ranked top-40 active cell types (mean rate over members, size, hop distance)
  * per-layer propagation R1-6 -> L1/L2/L3 -> Mi1/Tm3 -> T4/T5 -> LPLC2/LC4/LC6 -> DNp,
    with the BFS hop distance of each layer from the photoreceptors
  * first-spike time per layer (earliest, and median over the members that ever spike)
  * the MEAN-FIELD BUDGET per layer: measured net signed input S = sum_j W_ij r_j
    (synapse*Hz) and the steady-state depolarisation it implies,
        g_inf = w_syn * tau * 1e-3 * S = 1.375e-3 * S   [mV]
    against the 7.0 mV the model needs (v_th - v_0 = -45 - (-52)). A layer whose S is
    below ~5091 synapse*Hz can never reach threshold on mean drive alone.
  * total active count

Stimuli
  full_field   every R1-6 photoreceptor driven by Poisson at --bg-hz for the whole run
  disk         only the photoreceptors within --radius-deg of (--az, --el)
  dark_flash   full field for --t-on-ms, then drive removed (the sign-corrected "dark"
               transient: light is tonic, darkness is the REMOVAL of drive)

    python src/fly_diag_vision.py --bg-hz 40 --t-run-ms 400 --trials 10 \
        --stim full_field --out /media/llm-data/universe-runs/neuromod-lab-taxi/fly
"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.dynamics import LifBrain, LifParams
from flybrain.eye import photoreceptor_chart

ANNOTATIONS_TSV = '/media/llm-data/datasets/flywire/neuron_annotations.tsv'

# Layer regexes use the REAL cell_type spellings of the Schlegel et al. 2024 annotations,
# verified against the table (counts are printed at run time).
LAYERS = [
    ('R1-6', r'^R1-6$'), ('R7', r'^R7$'), ('R8', r'^R8$'),
    ('L1', r'^L1$'), ('L2', r'^L2$'), ('L3', r'^L3$'), ('L4', r'^L4$'), ('L5', r'^L5$'),
    ('Lai', r'^Lai$'), ('Lawf1', r'^Lawf1$'), ('Lawf2', r'^Lawf2$'),
    ('C2', r'^C2$'), ('C3', r'^C3$'), ('T1', r'^T1$'),
    ('Mi1', r'^Mi1$'), ('Mi4', r'^Mi4$'), ('Mi9', r'^Mi9$'),
    ('Tm1', r'^Tm1$'), ('Tm2', r'^Tm2$'), ('Tm3', r'^Tm3$'), ('Tm4', r'^Tm4$'),
    ('Tm9', r'^Tm9$'), ('Tm20', r'^Tm20$'), ('CT1', r'^CT1$'),
    ('T4', r'^T4[abcd]$'), ('T5', r'^T5[abcd]$'),
    ('LPLC1', r'^LPLC1$'), ('LPLC2', r'^LPLC2$'), ('LPLC4', r'^LPLC4$'),
    ('LC4', r'^LC4$'), ('LC6', r'^LC6$'), ('LC11', r'^LC11$'),
    ('HS', r'^HS[ENS]$'), ('VS', r'^VS[1-8]$'),
    ('DNp01', r'^DNp01$'), ('DNp02_09', r'^DNp0[2-9]$'), ('DNp_all', r'^DNp'),
]

G_NEEDED_MV = 7.0          # v_th - v_0 = -45 - (-52)


def bfs_hops(cm, src, max_hops=8):
    """Directed hop distance from `src` over every edge (sign ignored); -1 = unreachable."""
    indptr, cols, _ = cm.csr_by_pre()
    dist = np.full(cm.n, -1, dtype=np.int16)
    dist[src] = 0
    frontier = np.asarray(src, dtype=np.int64)
    for d in range(1, max_hops + 1):
        if frontier.size == 0:
            break
        starts, ends = indptr[frontier], indptr[frontier + 1]
        lens = ends - starts
        keep = lens > 0
        if not keep.any():
            break
        starts, lens = starts[keep], lens[keep]
        offs = np.arange(int(lens.sum())) - np.repeat(np.cumsum(lens) - lens, lens)
        nbrs = cols[np.repeat(starts, lens) + offs]
        nxt = np.unique(nbrs)
        nxt = nxt[dist[nxt] < 0]
        dist[nxt] = d
        frontier = nxt.astype(np.int64)
    return dist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bg-hz', type=float, default=40.0, help='Poisson rate on the driven photoreceptors')
    ap.add_argument('--t-run-ms', type=float, default=400.0)
    ap.add_argument('--t-on-ms', type=float, default=200.0, help='dark_flash: drive is removed after this')
    ap.add_argument('--trials', type=int, default=10)
    ap.add_argument('--stim', choices=['full_field', 'disk', 'dark_flash'], default='full_field')
    ap.add_argument('--az', type=float, default=30.0)
    ap.add_argument('--el', type=float, default=0.0)
    ap.add_argument('--radius-deg', type=float, default=20.0)
    ap.add_argument('--drive-type', default=r'^R1-6$',
                    help='regex on cell_type of the neurons that receive the Poisson drive; '
                         'use it to inject downstream (e.g. "^L[12]$") and test the rest of the path')
    ap.add_argument('--tag', default='')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)

    cm = load_connectome()
    ct = cm.neurons['cell_type'].to_numpy()
    print(f'[map] {cm.summary()}', flush=True)

    drive_idx = np.flatnonzero(cm.neurons['cell_type'].str.match(a.drive_type).to_numpy())
    if drive_idx.size == 0:
        raise SystemExit(f'no neuron matches --drive-type {a.drive_type!r}')
    photo = np.flatnonzero(ct == 'R1-6')
    hops = bfs_hops(cm, drive_idx)

    if a.stim == 'disk':
        chart = photoreceptor_chart(cm, ANNOTATIONS_TSV)
        d = np.hypot(chart['azimuth_deg'].to_numpy() - a.az, chart['elevation_deg'].to_numpy() - a.el)
        sel = chart['index'].to_numpy()[d <= a.radius_deg]
        drive_idx = np.intersect1d(drive_idx, sel)
        print(f'[stim] disk at (az {a.az:+.0f}, el {a.el:+.0f}) r {a.radius_deg:.0f} deg '
              f'-> {drive_idx.size} of {photo.size} photoreceptors', flush=True)
    print(f'[stim] {a.stim}  driving {drive_idx.size} neurons matching {a.drive_type!r} at {a.bg_hz:.0f} Hz '
          f'for {a.t_run_ms:.0f} ms, {a.trials} trials', flush=True)

    dev = 'cuda'
    brain = LifBrain(cm, a.trials, LifParams(), device=dev)
    brain.set_poisson(drive_idx, a.bg_hz)
    dt = brain.p.dt
    steps = int(round(a.t_run_ms / dt))
    off_step = int(round(a.t_on_ms / dt)) if a.stim == 'dark_flash' else steps

    first_step = torch.full((cm.n,), -1, device=dev, dtype=torch.int32)
    snap_every = max(1, int(round(25.0 / dt)))
    snaps, snap_t = [], []
    t0 = time.time()
    for k in range(steps):
        if k == off_step:                                   # dark: remove the tonic drive
            brain.poisson_p = 0.0
            print(f'  [t={k * dt:.0f} ms] drive OFF', flush=True)
        spk = brain.step()
        fired = spk.any(0)
        first_step = torch.where(fired & (first_step < 0), torch.full_like(first_step, k), first_step)
        if (k + 1) % snap_every == 0:
            snaps.append(brain.spike_count.sum(0).clone())
            snap_t.append((k + 1) * dt)
    torch.cuda.synchronize()
    wall = time.time() - t0

    rates = brain.rates_hz().cpu().numpy()
    first_ms = first_step.cpu().numpy().astype(np.float32)
    first_ms[first_ms < 0] = np.nan
    first_ms *= dt
    snaps = torch.stack(snaps).cpu().numpy() if snaps else np.zeros((0, cm.n))
    active = int((rates > 0).sum())
    del brain
    torch.cuda.empty_cache()

    # ---- mean-field budget: S_i = sum_j W_ij r_j (synapse*Hz), on the GPU ------------------
    rt = torch.as_tensor(rates, device=dev)
    pre_t = torch.as_tensor(cm.pre.astype(np.int64), device=dev)
    post_t = torch.as_tensor(cm.post.astype(np.int64), device=dev)
    w_t = torch.as_tensor(cm.weight.astype(np.float32), device=dev)
    s_net = torch.zeros(cm.n, device=dev)
    s_exc = torch.zeros(cm.n, device=dev)
    s_inh = torch.zeros(cm.n, device=dev)
    contrib = w_t * rt[pre_t]
    s_net.index_add_(0, post_t, contrib)
    s_exc.index_add_(0, post_t, torch.clamp(contrib, min=0))
    s_inh.index_add_(0, post_t, torch.clamp(contrib, max=0))
    s_net, s_exc, s_inh = s_net.cpu().numpy(), s_exc.cpu().numpy(), s_inh.cpu().numpy()
    del pre_t, post_t, w_t, contrib, rt
    torch.cuda.empty_cache()
    k_mv = LifParams().w_syn * LifParams().tau * 1e-3        # 1.375e-3 mV per synapse*Hz

    # ---- per-layer table --------------------------------------------------------------------
    layers = []
    for name, pat in LAYERS:
        idx = np.flatnonzero(cm.neurons['cell_type'].str.match(pat).to_numpy())
        if idx.size == 0:
            layers.append(dict(layer=name, regex=pat, n=0)); continue
        fm = first_ms[idx]
        h = hops[idx]
        layers.append(dict(
            layer=name, regex=pat, n=int(idx.size),
            hops_median=float(np.median(h[h >= 0])) if (h >= 0).any() else None,
            reachable_frac=float((h >= 0).mean()),
            rate_hz=float(rates[idx].mean()), rate_max_hz=float(rates[idx].max()),
            frac_active=float((rates[idx] > 0).mean()),
            first_spike_ms=float(np.nanmin(fm)) if np.isfinite(fm).any() else None,
            first_spike_median_ms=float(np.nanmedian(fm)) if np.isfinite(fm).any() else None,
            s_net_syn_hz=float(s_net[idx].mean()), s_exc_syn_hz=float(s_exc[idx].mean()),
            s_inh_syn_hz=float(s_inh[idx].mean()),
            g_inf_mv=float(s_net[idx].mean() * k_mv), g_inf_max_mv=float(s_net[idx].max() * k_mv)))

    print(f'\n--- propagation ({a.stim}, {a.bg_hz:.0f} Hz, {a.t_run_ms:.0f} ms, {a.trials} trials) ---')
    print(f'{"layer":9s} {"n":>6s} {"hop":>4s} {"rate Hz":>9s} {"max Hz":>8s} {"act%":>6s} '
          f'{"1st ms":>7s} {"S_net":>10s} {"S_exc":>10s} {"S_inh":>10s} {"g_inf mV":>9s}')
    for L in layers:
        if L['n'] == 0:
            print(f'{L["layer"]:9s} {"ABSENT":>6s}'); continue
        fs = f'{L["first_spike_ms"]:7.1f}' if L['first_spike_ms'] is not None else f'{"-":>7s}'
        hp = f'{L["hops_median"]:4.0f}' if L['hops_median'] is not None else f'{"-":>4s}'
        print(f'{L["layer"]:9s} {L["n"]:6d} {hp} {L["rate_hz"]:9.2f} {L["rate_max_hz"]:8.1f} '
              f'{100 * L["frac_active"]:5.1f}% {fs} {L["s_net_syn_hz"]:10.0f} {L["s_exc_syn_hz"]:10.0f} '
              f'{L["s_inh_syn_hz"]:10.0f} {L["g_inf_mv"]:9.2f}')
    print(f'(threshold needs g_inf >= {G_NEEDED_MV:.1f} mV, i.e. S_net >= {G_NEEDED_MV / k_mv:.0f} synapse*Hz)')

    # ---- ranked active cell types -------------------------------------------------------------
    order = np.argsort(ct)
    ct_sorted = ct[order]
    bounds = np.flatnonzero(np.r_[True, ct_sorted[1:] != ct_sorted[:-1], True])
    ranked = []
    for s, e in zip(bounds[:-1], bounds[1:]):
        idx = order[s:e]
        if idx.size < 3 or ct_sorted[s] == '':
            continue
        r = rates[idx]
        if r.mean() <= 0:
            continue
        h = hops[idx]
        ranked.append(dict(cell_type=str(ct_sorted[s]), n=int(idx.size), rate_hz=float(r.mean()),
                           frac_active=float((r > 0).mean()),
                           hops_median=float(np.median(h[h >= 0])) if (h >= 0).any() else None,
                           first_spike_ms=float(np.nanmin(first_ms[idx])) if np.isfinite(first_ms[idx]).any() else None))
    ranked.sort(key=lambda d: -d['rate_hz'])
    print(f'\n--- top 40 active cell types (>= 3 neurons), of {len(ranked)} types with any activity ---')
    print(f'{"rank":>4s} {"cell_type":16s} {"n":>6s} {"rate Hz":>9s} {"act%":>6s} {"hop":>4s} {"1st ms":>7s}')
    for i, d in enumerate(ranked[:40]):
        hp = f'{d["hops_median"]:4.0f}' if d['hops_median'] is not None else f'{"-":>4s}'
        fs = f'{d["first_spike_ms"]:7.1f}' if d['first_spike_ms'] is not None else f'{"-":>7s}'
        print(f'{i + 1:4d} {d["cell_type"][:16]:16s} {d["n"]:6d} {d["rate_hz"]:9.2f} '
              f'{100 * d["frac_active"]:5.1f}% {hp} {fs}')

    non_drive_active = int((rates > 0).sum() - (rates[drive_idx] > 0).sum())
    print(f'\nactive neurons {active} ({drive_idx.size} driven, {non_drive_active} downstream), '
          f'{wall:.1f}s wall for {a.trials} trials x {a.t_run_ms:.0f} ms')

    # ---- time course of the layers that matter -------------------------------------------------
    course = {}
    for name in ['R1-6', 'L1', 'L2', 'L3', 'Mi1', 'Tm3', 'T4', 'T5', 'LPLC2', 'LC4', 'DNp01']:
        pat = dict(LAYERS)[name]
        idx = np.flatnonzero(cm.neurons['cell_type'].str.match(pat).to_numpy())
        if idx.size == 0 or snaps.size == 0:
            continue
        cum = snaps[:, idx].sum(1) / (a.trials * idx.size)
        course[name] = [float(x) for x in np.diff(np.r_[0.0, cum]) / (snap_every * dt * 1e-3)]
    print(f'\n--- rate (Hz) per 25 ms bin ---\n{"layer":9s} ' + ' '.join(f'{t:6.0f}' for t in snap_t))
    for name, c in course.items():
        print(f'{name:9s} ' + ' '.join(f'{x:6.1f}' for x in c))

    tag = a.tag or f'{a.stim}_{int(a.bg_hz)}hz'
    res = dict(args=vars(a), n_driven=int(drive_idx.size), active_neurons=active,
               downstream_active=non_drive_active, wall_s=wall, steps=steps,
               g_needed_mv=G_NEEDED_MV, s_needed_syn_hz=float(G_NEEDED_MV / k_mv),
               layers=layers, top_types=ranked[:40], bins_ms=snap_t, course_hz=course)
    path = os.path.join(a.out, f'fly_diag_vision_{tag}.json')
    with open(path, 'w') as f:
        json.dump(res, f, indent=1)
    print(f'\nwrote {path}')


if __name__ == '__main__':
    main()
