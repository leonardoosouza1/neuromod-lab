"""Export the FlyWire map (plus selection tables) to the `flymap` v1 binary read by Universe.

    python src/fly_export.py --out-dir /media/llm-data/datasets/flywire [--min-weight 3] [--exclude-optic]
                             [--shuffle-targets SEED] [--name flymap_783]

Groups follow flybrain.io_map: afferent cell types with >= 4 neurons are the input groups
(k_in), efferent cell types with >= 2 neurons are the output groups (k_out); cell-type ids
cover every neuron (unnamed types fall back to class?super_class).
"""
import argparse, hashlib, os, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from flybrain import load_connectome
from flybrain.connectome import type_key
from flybrain.flymap_file import NONE, write_flymap
from flybrain.selection import shuffle_targets


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', default='/media/llm-data/datasets/flywire')
    ap.add_argument('--name', default=None)
    ap.add_argument('--min-weight', type=int, default=1)
    ap.add_argument('--exclude-optic', action='store_true')
    ap.add_argument('--shuffle-targets', type=int, default=None, help='seed; degree-preserving shuffled control map')
    a = ap.parse_args()
    t0 = time.time()
    cm = load_connectome()
    if a.shuffle_targets is not None:
        cm = shuffle_targets(cm, a.shuffle_targets)
    keep = np.abs(cm.weight) >= a.min_weight
    if a.exclude_optic:
        non_optic = (cm.neurons['super_class'].to_numpy() != 'optic')
        keep &= non_optic[cm.pre] & non_optic[cm.post]
    pre, post, w = cm.pre[keep], cm.post[keep], cm.weight[keep].astype(np.float32)
    order = np.argsort(post, kind='stable')
    indptr = np.zeros(cm.n + 1, np.int64); np.add.at(indptr, post + 1, 1); indptr = np.cumsum(indptr)
    type_of, type_names, in_group_of, in_names, out_indptr, out_members, out_names = build_tables(cm)
    name = a.name or ('flymap_783' + (f'_w{a.min_weight}' if a.min_weight > 1 else '') + ('_nooptic' if a.exclude_optic else '')
                      + (f'_shuf{a.shuffle_targets}' if a.shuffle_targets is not None else ''))
    path = os.path.join(a.out_dir, name + '.bin')
    src = os.path.join('/media/llm-data/datasets/flywire', 'Connectivity_783.parquet')
    sidecar = dict(name=name, n=int(cm.n), m=int(len(pre)), n_types=len(type_names), k_in=len(in_names), k_out=len(out_names),
                   min_weight=a.min_weight, exclude_optic=a.exclude_optic, shuffle_targets=a.shuffle_targets,
                   synapses=int(np.abs(w).sum()), source=src, source_sha256=hashlib.sha256(open(src, 'rb').read()).hexdigest(),
                   type_names=type_names, in_group_names=in_names, out_group_names=out_names)
    write_flymap(path, indptr.astype(np.uint32), pre[order].astype(np.uint32), w[order], type_of, in_group_of, out_indptr, out_members, sidecar)
    print(f'{path}: n {cm.n} m {len(pre)} types {len(type_names)} k_in {len(in_names)} k_out {len(out_names)} '
          f'{os.path.getsize(path) / 1e6:.0f} MB in {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
