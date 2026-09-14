"""`flymap` v1/v2 binary — the map as consumed by Universe (`docs/96-flymap-v2.md`,
Universe `docs/FLY-MAP-BRAIN.md` §1, `docs/KERNELS-FLY-SPIKING.md`).

Little-endian throughout.

v1 (magic b'FLYMAP01'): 8 u32 header (n, m, n_types, k_in, k_out, out_members_len, 0, 0),
then indptr u32[n+1] (CSR rows = POSTsynaptic neuron), indices u32[m] (presynaptic),
weights f32[m], type_of u32[n], in_group_of u32[n] (NONE = 0xFFFFFFFF), out_indptr
u32[k_out+1], out_members u32[out_members_len]. Names live in the sidecar JSON.

v2 (magic b'FLYMAP02'): byte-identical to v1 up to the end of `out_members`, except that
header word 6 (0-based, byte offset 32) carries a FLAG WORD (word 7 / byte offset 36
stays reserved, always 0). Each flag adds one trailing block, in this order:
  bit 0 FLAG_PRE_CSR         pre_indptr u32[n+1], pre_indices u32[m] (the POSTsynaptic
                             partner of each edge), pre_weights f32[m] — the same edge
                             multiset as the v1 CSR, sorted by PREsynaptic neuron (what
                             an event-driven spiking kernel walks).
  bit 1 FLAG_PIXEL_BINDING   pixel_of_neuron u32[n] — rendered-retina pixel index
                             (row-major, row * cols + col) driving each neuron, NONE for
                             every neuron not bound to a pixel (built by
                             `flybrain.eye.pixel_of_neuron` from either a photoreceptor
                             chart or a motion-detector chart — the exporter's
                             `--eye-target` decides which).
  bit 2 FLAG_NO_REFRACTORY   no_refractory u32[ceil(n/32)] — bitmap, LSB-first within each
                             word (bit `i & 31` of word `i >> 5`): neuron i is a Poisson /
                             driven target whose refractory period is zeroed. Set for
                             every neuron with a pixel binding.
Writing without any optional block produces a v1 file, byte-identical to the v1 writer.
"""
from __future__ import annotations

import json
import os

import numpy as np

MAGIC_V1 = b'FLYMAP01'
MAGIC_V2 = b'FLYMAP02'
MAGIC = MAGIC_V1                      # kept for callers that imported the v1 name
NONE = 0xFFFFFFFF

FLAG_PRE_CSR = 1 << 0
FLAG_PIXEL_BINDING = 1 << 1
FLAG_NO_REFRACTORY = 1 << 2


def pack_bitmap(mask, n: int | None = None) -> np.ndarray:
    """bool[n] -> u32[ceil(n/32)], bit `i & 31` of word `i >> 5` (LSB-first)."""
    mask = np.asarray(mask, dtype=bool)
    n = len(mask) if n is None else n
    words = np.zeros((n + 31) // 32, dtype='<u4')
    idx = np.flatnonzero(mask)
    np.bitwise_or.at(words, idx >> 5, (np.uint32(1) << (idx & 31).astype(np.uint32)))
    return words


def unpack_bitmap(words, n: int) -> np.ndarray:
    """u32[ceil(n/32)] -> bool[n] (inverse of `pack_bitmap`)."""
    words = np.asarray(words, dtype=np.uint32)
    i = np.arange(n, dtype=np.uint32)
    return ((words[i >> 5] >> (i & 31)) & 1).astype(bool)


def write_flymap(path, indptr, indices, weights, type_of, in_group_of, out_indptr, out_members,
                 sidecar: dict | None = None, pre_indptr=None, pre_indices=None, pre_weights=None,
                 pixel_of_neuron=None, no_refractory=None):
    """Write a flymap. With no optional block this is byte-identical to the v1 writer."""
    n, m = len(indptr) - 1, len(indices)
    k_out = len(out_indptr) - 1
    k_in = int(sidecar.get('k_in', 0)) if sidecar else int(in_group_of[in_group_of != NONE].max() + 1 if (in_group_of != NONE).any() else 0)
    n_types = int(sidecar.get('n_types', 0)) if sidecar else int(type_of.max() + 1)
    assert len(weights) == m and len(type_of) == n and len(in_group_of) == n and out_members.max(initial=0) < n
    blocks, flags = [], 0
    if pre_indptr is not None or pre_indices is not None or pre_weights is not None:
        assert pre_indptr is not None and pre_indices is not None and pre_weights is not None, 'presynaptic CSR is all three arrays or none'
        assert len(pre_indptr) == n + 1 and len(pre_indices) == m and len(pre_weights) == m, 'presynaptic CSR must cover the same n and m'
        flags |= FLAG_PRE_CSR
        blocks += [(pre_indptr, '<u4'), (pre_indices, '<u4'), (pre_weights, '<f4')]
    if pixel_of_neuron is not None:
        assert len(pixel_of_neuron) == n, 'pixel_of_neuron is one entry per neuron'
        flags |= FLAG_PIXEL_BINDING
        blocks.append((pixel_of_neuron, '<u4'))
    if no_refractory is not None:
        words = pack_bitmap(no_refractory) if len(no_refractory) == n and np.asarray(no_refractory).dtype == bool else np.asarray(no_refractory, dtype='<u4')
        assert len(words) == (n + 31) // 32, 'no_refractory must be bool[n] or u32[ceil(n/32)]'
        flags |= FLAG_NO_REFRACTORY
        blocks.append((words, '<u4'))
    with open(path, 'wb') as f:
        f.write(MAGIC_V2 if flags else MAGIC_V1)
        np.array([n, m, n_types, k_in, k_out, len(out_members), flags, 0], dtype='<u4').tofile(f)
        for arr, dt in ([(indptr, '<u4'), (indices, '<u4'), (weights, '<f4'), (type_of, '<u4'), (in_group_of, '<u4'),
                         (out_indptr, '<u4'), (out_members, '<u4')] + blocks):
            np.ascontiguousarray(arr, dtype=dt).tofile(f)
    if sidecar is not None:
        with open(os.path.splitext(path)[0] + '.json', 'w') as f:
            json.dump(sidecar, f, indent=1)


def read_flymap(path):
    """Read a v1 or v2 flymap; optional blocks appear in the dict only when their flag is set."""
    with open(path, 'rb') as f:
        magic = f.read(8)
        assert magic in (MAGIC_V1, MAGIC_V2), f'not a flymap file: {magic!r}'
        n, m, n_types, k_in, k_out, oml, flags, _reserved = np.fromfile(f, '<u4', 8)
        version = 1 if magic == MAGIC_V1 else 2
        flags = int(flags) if version == 2 else 0
        out = dict(n=int(n), m=int(m), n_types=int(n_types), k_in=int(k_in), k_out=int(k_out),
                   version=version, flags=flags)
        out['indptr'] = np.fromfile(f, '<u4', n + 1)
        out['indices'] = np.fromfile(f, '<u4', m)
        out['weights'] = np.fromfile(f, '<f4', m)
        out['type_of'] = np.fromfile(f, '<u4', n)
        out['in_group_of'] = np.fromfile(f, '<u4', n)
        out['out_indptr'] = np.fromfile(f, '<u4', k_out + 1)
        out['out_members'] = np.fromfile(f, '<u4', oml)
        if flags & FLAG_PRE_CSR:
            out['pre_indptr'] = np.fromfile(f, '<u4', n + 1)
            out['pre_indices'] = np.fromfile(f, '<u4', m)
            out['pre_weights'] = np.fromfile(f, '<f4', m)
        if flags & FLAG_PIXEL_BINDING:
            out['pixel_of_neuron'] = np.fromfile(f, '<u4', n)
        if flags & FLAG_NO_REFRACTORY:
            out['no_refractory'] = np.fromfile(f, '<u4', (int(n) + 31) // 32)
        assert f.read(1) == b'', 'trailing bytes'
    for key in ('indptr', 'indices', 'weights', 'type_of', 'in_group_of', 'out_indptr', 'out_members'):
        assert len(out[key]) > 0 or (key == 'out_members' and oml == 0), f'truncated block {key}'
    return out
