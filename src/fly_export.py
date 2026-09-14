"""Export the FlyWire map (plus selection tables) to the `flymap` binary read by Universe.

    python src/fly_export.py --out-dir /media/llm-data/datasets/flywire [--min-weight 3] [--exclude-optic]
                             [--shuffle-targets SEED] [--name flymap_783] [--eye-target photoreceptor|motion]
                             [--eye-fit strip|stretch] [--retina-rows 14] [--retina-cols 126] [--fov-deg 120]
                             [--max-pitch-rad -0.06] [--no-pre-csr] [--no-eye]

Writes v2 by default (`docs/96-flymap-v2.md`): the v1 blocks plus the presynaptic CSR, the
eye/motion-detector -> pixel binding and the no-refractory bitmap. `--no-pre-csr --no-eye` writes
a v1 file, byte-identical to what the v1 exporter produced.

`--eye-target photoreceptor` (default) binds the R1-6 photoreceptors — the right target for the
RATE brain, which handles the eye's graded, non-spiking early stages. `--eye-target motion` binds
the T4/T5 motion detectors instead — the right target for the SPIKING brain: a measurement on
14/09/2026 found the optic lobe does not propagate under LIF (the medulla is net inhibitory),
while driving T4/T5 directly reaches LPLC2, HS/VS and the giant fiber DNp01 (see `flybrain/eye.py`
and `PREDICOES.md` #189v).

Groups follow flybrain.io_map: afferent cell types with >= 4 neurons are the input groups
(k_in), efferent cell types with >= 2 neurons are the output groups (k_out); cell-type ids
cover every neuron (unnamed types fall back to class?super_class).
"""
import argparse, hashlib, os, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.connectome import ROOT_DEFAULT, type_key
from flybrain.eye import (RETINA_COLS, RETINA_FOV_DEG, RETINA_MAX_PITCH_RAD, RETINA_MIN_PITCH_RAD, RETINA_ROWS,
                          motion_chart, photoreceptor_chart, pixel_of_neuron)
from flybrain.flymap_file import (FLAG_NO_REFRACTORY, FLAG_PIXEL_BINDING, FLAG_PRE_CSR, FLAG_REFLEX_READOUT,
                                   NONE, write_flymap)


REFLEX_GROUPS = {
    'REFLEX_STEER_RIGHT': (r'^(HS|VS)', 'right'),
    'REFLEX_STEER_LEFT': (r'^(HS|VS)', 'left'),
    'REFLEX_LOOM': (r'^LPLC2$', None),
    'REFLEX_LOOM_CONTROL': (r'^LC1[01]', None),
}


def reflex_tables(cm, out_names, out_indptr, out_members):
    """Append the four anatomical readout groups and the (plus, minus) triples that use them.

    Measured 14/09/2026 (predictions 191v and 193v): driving the motion detectors on one side of the
    visual field swings the HS/VS asymmetry by +2.000 in the spiking model and +1.74/+1.92 in the rate
    model the Universe kernel runs, and the swing disappears on a degree-preserving shuffled map. So
    steer = mean(HS+VS on the right) - mean(HS+VS on the left) is a reflex the animal already has.
    Brake is looming (LPLC2) above a same-order visual-projection baseline (LC10/LC11, small-object
    cells that do not respond to expansion). Throttle is NONE: the host supplies a fixed cruise, so
    the experiment measures steering, not speed control.
    """
    nrn = cm.neurons
    names = list(out_names)
    indptr = list(out_indptr)
    members = list(out_members)
    for name, (regex, side) in REFLEX_GROUPS.items():
        sel = nrn['cell_type'].str.match(regex).to_numpy().copy()
        if side is not None:
            sel &= (nrn['side'].to_numpy() == side)
        idx = np.flatnonzero(sel)
        assert len(idx) > 0, f'reflex group {name} is empty'
        names.append(name)
        members.extend(idx.tolist())
        indptr.append(len(members))
    g = {name: names.index(name) for name in REFLEX_GROUPS}
    reflex_out = np.array([NONE, NONE,                                   # throttle: host-supplied
                           g['REFLEX_STEER_RIGHT'], g['REFLEX_STEER_LEFT'],
                           g['REFLEX_LOOM'], g['REFLEX_LOOM_CONTROL']], dtype=np.uint32)
    return names, np.array(indptr, np.uint32), np.array(members, np.uint32), reflex_out


def build_tables(cm):
    nrn = cm.neurons
    key = type_key(nrn)
    type_names, type_of = np.unique(key, return_inverse=True)
    in_group_of = np.full(cm.n, NONE, dtype=np.uint32)
    aff = np.flatnonzero(nrn['flow'].to_numpy() == 'afferent')
    in_names = []
    for name, members in _groups(key, aff, min_size=4):
        in_group_of[members] = len(in_names); in_names.append(name)
    eff = np.flatnonzero(nrn['flow'].to_numpy() == 'efferent')
    out_names, out_indptr, out_members = [], [0], []
    for name, members in _groups(key, eff, min_size=2):
        out_names.append(name); out_members.extend(members.tolist()); out_indptr.append(len(out_members))
    return (type_of.astype(np.uint32), list(map(str, type_names)), in_group_of, in_names,
            np.array(out_indptr, np.uint32), np.array(out_members, np.uint32), out_names)


def _groups(type_key, idx, min_size):
    keys = type_key[idx]
    for name in sorted(set(keys)):
        members = idx[keys == name]
        if len(members) >= min_size:
            yield name, members


def csr(rows, cols, vals, n):
    """CSR of the same edge multiset keyed on `rows`: (indptr u32[n+1], cols u32[m], vals f32[m])."""
    order = np.argsort(rows, kind='stable')
    indptr = np.zeros(n + 1, np.int64); np.add.at(indptr, rows + 1, 1)
    return np.cumsum(indptr).astype(np.uint32), cols[order].astype(np.uint32), vals[order].astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', default=ROOT_DEFAULT)
    ap.add_argument('--name', default=None)
    ap.add_argument('--min-weight', type=int, default=1)
    ap.add_argument('--exclude-optic', action='store_true')
    ap.add_argument('--shuffle-targets', type=int, default=None, help='seed; degree-preserving shuffled control map')
    ap.add_argument('--no-pre-csr', action='store_true', help='skip the presynaptic CSR block (half the file size)')
    ap.add_argument('--no-eye', action='store_true', help='skip the pixel binding and no-refractory blocks')
    ap.add_argument('--no-reflex', action='store_true', help='skip the anatomical reflex readout block')
    ap.add_argument('--eye-target', choices=['photoreceptor', 'motion'], default='photoreceptor',
                    help='photoreceptor: R1-6, for the rate brain. motion: T4+T5, for the spiking brain '
                         '(the optic lobe does not propagate photoreceptor drive under LIF)')
    ap.add_argument('--retina-rows', type=int, default=RETINA_ROWS)
    ap.add_argument('--retina-cols', type=int, default=RETINA_COLS)
    ap.add_argument('--fov-deg', type=float, default=RETINA_FOV_DEG)
    ap.add_argument('--min-pitch-rad', type=float, default=RETINA_MIN_PITCH_RAD, help='elevation of retina row 0')
    ap.add_argument('--max-pitch-rad', type=float, default=RETINA_MAX_PITCH_RAD, help='elevation of the last retina row')
    ap.add_argument('--eye-fit', choices=['strip', 'stretch'], default='stretch',
                    help='strip: true angles, only receptors looking inside the rendered window are bound '
                         '(~1%% of the eye). stretch (default): the whole chart is mapped onto the retina, '
                         'so every charted neuron is used.')
    a = ap.parse_args()
    t0 = time.time()
    cm = load_connectome()
    keep = np.abs(cm.weight) >= a.min_weight
    if a.exclude_optic:
        non_optic = (cm.neurons['super_class'].to_numpy() != 'optic')
        keep &= non_optic[cm.pre] & non_optic[cm.post]
    pre, post, w = cm.pre[keep], cm.post[keep], cm.weight[keep].astype(np.float32)
    if a.shuffle_targets is not None:
        # control map: permute the postsynaptic endpoints AMONG THE KEPT EDGES, so the shuffled map has
        # exactly the same edge count, out-degrees, in-degrees and signs as the real map it controls for
        post = post[np.random.default_rng(a.shuffle_targets).permutation(len(post))]
    indptr, indices, weights = csr(post, pre, w, cm.n)                  # v1 CSR: rows = postsynaptic
    pre_csr = (None, None, None) if a.no_pre_csr else csr(pre, post, w, cm.n)   # rows = presynaptic
    type_of, type_names, in_group_of, in_names, out_indptr, out_members, out_names = build_tables(cm)
    reflex_out = None
    if not a.no_reflex:
        out_names, out_indptr, out_members, reflex_out = reflex_tables(cm, out_names, out_indptr, out_members)

    pixel_of, no_rfc = None, None
    n_eye = n_bound = n_bound_strip = n_bound_stretch = 0
    if not a.no_eye:
        annotations_tsv = os.path.join(ROOT_DEFAULT, 'neuron_annotations.tsv')
        chart = (photoreceptor_chart if a.eye_target == 'photoreceptor' else motion_chart)(cm, annotations_tsv)
        fit_kw = dict(rows=a.retina_rows, cols=a.retina_cols, fov_deg=a.fov_deg,
                     min_pitch_rad=a.min_pitch_rad, max_pitch_rad=a.max_pitch_rad)
        pixel_of = pixel_of_neuron(chart, cm.n, fit=a.eye_fit, **fit_kw)
        assert (pixel_of[pixel_of != NONE] < a.retina_rows * a.retina_cols).all(), 'pixel index outside the retina'
        no_rfc = pixel_of != NONE                                  # driven neurons run without a refractory period
        n_eye, n_bound = len(chart), int(no_rfc.sum())
        # report both fits regardless of which one is exported (docs/96-flymap-v2.md wants both numbers)
        n_bound_strip = int((pixel_of_neuron(chart, cm.n, fit='strip', **fit_kw) != NONE).sum())
        n_bound_stretch = int((pixel_of_neuron(chart, cm.n, fit='stretch', **fit_kw) != NONE).sum())

    v2 = not (a.no_pre_csr and a.no_eye and a.no_reflex)
    name = a.name or ('flymap_783' + (f'_w{a.min_weight}' if a.min_weight > 1 else '') + ('_nooptic' if a.exclude_optic else '')
                      + (f'_shuf{a.shuffle_targets}' if a.shuffle_targets is not None else '')
                      + ('_motion' if (not a.no_eye and a.eye_target == 'motion') else '')
                      + ('_v2' if v2 else ''))
    path = os.path.join(a.out_dir, name + '.bin')
    src = os.path.join(ROOT_DEFAULT, 'Connectivity_783.parquet')
    flags = ((0 if a.no_pre_csr else FLAG_PRE_CSR) | (0 if a.no_eye else FLAG_PIXEL_BINDING | FLAG_NO_REFRACTORY)
             | (0 if a.no_reflex else FLAG_REFLEX_READOUT))
    sidecar = dict(name=name, format_version=2 if v2 else 1, flags=flags,
                   n=int(cm.n), m=int(len(pre)), n_types=len(type_names), k_in=len(in_names), k_out=len(out_names),
                   min_weight=a.min_weight, exclude_optic=a.exclude_optic, shuffle_targets=a.shuffle_targets,
                   pre_csr=not a.no_pre_csr, eye_target=None if a.no_eye else a.eye_target,
                   eye_fit=None if a.no_eye else a.eye_fit,
                   retina=None if a.no_eye else dict(rows=a.retina_rows, cols=a.retina_cols, fov_deg=a.fov_deg,
                                                     min_pitch_rad=a.min_pitch_rad, max_pitch_rad=a.max_pitch_rad,
                                                     warp_row0=True, source='Universe src/config.rs + src/gpu/retina.wgsl'),
                   eye_neurons_total=n_eye, eye_neurons_bound=n_bound,
                   eye_neurons_bound_strip=n_bound_strip, eye_neurons_bound_stretch=n_bound_stretch,
                   synapses=int(np.abs(w).sum()), source=src, source_sha256=hashlib.sha256(open(src, 'rb').read()).hexdigest(),
                   type_names=type_names, in_group_names=in_names, out_group_names=out_names,
                   reflex_out=None if reflex_out is None else [int(v) for v in reflex_out],
                   reflex_groups=None if reflex_out is None else {n: int(out_indptr[out_names.index(n) + 1] - out_indptr[out_names.index(n)]) for n in REFLEX_GROUPS})
    write_flymap(path, indptr, indices, weights, type_of, in_group_of, out_indptr, out_members, sidecar,
                 pre_indptr=pre_csr[0], pre_indices=pre_csr[1], pre_weights=pre_csr[2],
                 pixel_of_neuron=pixel_of, no_refractory=no_rfc, reflex_out=reflex_out)
    print(f'{path}: v{sidecar["format_version"]} flags 0x{flags:x} n {cm.n} m {len(pre)} types {len(type_names)} '
          f'k_in {len(in_names)} k_out {len(out_names)} eye_target {a.eye_target if not a.no_eye else "none"} '
          f'bound {n_bound}/{n_eye} ({a.eye_fit}) [strip {n_bound_strip} stretch {n_bound_stretch}] '
          f'{os.path.getsize(path) / 1e6:.0f} MB in {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
