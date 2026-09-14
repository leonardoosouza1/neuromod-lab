"""`flymap` v1 binary — the map as consumed by Universe (`docs/FLY-MAP-BRAIN.md` §1).

Little-endian: magic b'FLYMAP01', 8 u32 header (n, m, n_types, k_in, k_out, out_members_len,
0, 0), then indptr u32[n+1] (CSR rows = POSTsynaptic neuron), indices u32[m] (presynaptic),
weights f32[m], type_of u32[n], in_group_of u32[n] (NONE = 0xFFFFFFFF), out_indptr
u32[k_out+1], out_members u32[out_members_len]. Names live in the sidecar JSON.
"""
from __future__ import annotations

import json
import os

import numpy as np

MAGIC = b'FLYMAP01'
NONE = 0xFFFFFFFF


def write_flymap(path, indptr, indices, weights, type_of, in_group_of, out_indptr, out_members, sidecar: dict | None = None):
    n, m = len(indptr) - 1, len(indices)
    k_out = len(out_indptr) - 1
    k_in = int(sidecar.get('k_in', 0)) if sidecar else int(in_group_of[in_group_of != NONE].max() + 1 if (in_group_of != NONE).any() else 0)
    n_types = int(sidecar.get('n_types', 0)) if sidecar else int(type_of.max() + 1)
    assert len(weights) == m and len(type_of) == n and len(in_group_of) == n and out_members.max(initial=0) < n
    with open(path, 'wb') as f:
        f.write(MAGIC)
        np.array([n, m, n_types, k_in, k_out, len(out_members), 0, 0], dtype='<u4').tofile(f)
        for arr, dt in ((indptr, '<u4'), (indices, '<u4'), (weights, '<f4'), (type_of, '<u4'), (in_group_of, '<u4'),
                        (out_indptr, '<u4'), (out_members, '<u4')):
            np.ascontiguousarray(arr, dtype=dt).tofile(f)
    if sidecar is not None:
        with open(os.path.splitext(path)[0] + '.json', 'w') as f:
            json.dump(sidecar, f, indent=1)


def read_flymap(path):
    with open(path, 'rb') as f:
        assert f.read(8) == MAGIC, 'not a flymap v1 file'
        n, m, n_types, k_in, k_out, oml, _, _ = np.fromfile(f, '<u4', 8)
        out = dict(n=int(n), m=int(m), n_types=int(n_types), k_in=int(k_in), k_out=int(k_out))
        out['indptr'] = np.fromfile(f, '<u4', n + 1)
        out['indices'] = np.fromfile(f, '<u4', m)
        out['weights'] = np.fromfile(f, '<f4', m)
        out['type_of'] = np.fromfile(f, '<u4', n)
        out['in_group_of'] = np.fromfile(f, '<u4', n)
        out['out_indptr'] = np.fromfile(f, '<u4', k_out + 1)
        out['out_members'] = np.fromfile(f, '<u4', oml)
        assert f.read(1) == b'', 'trailing bytes'
    return out
