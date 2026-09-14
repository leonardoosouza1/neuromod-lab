"""Load the FlyWire v783 map (as packaged by Shiu et al. 2024) plus the cell-type
annotations (Schlegel et al. 2024) into aligned arrays, cached as npz/parquet.

Files expected under `root` (default /media/llm-data/datasets/flywire):
  Completeness_783.csv      index = root_id, 138 639 rows — defines neuron index order
  Connectivity_783.parquet  15 091 983 rows: Presynaptic_Index, Postsynaptic_Index,
                            Connectivity (synapse count), Excitatory (+1/-1),
                            'Excitatory x Connectivity' (signed count = the weight)
  neuron_annotations.tsv    139 248 rows: root_id, super_class, flow, cell_class, ...
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

ROOT_DEFAULT = '/media/llm-data/datasets/flywire'
ANNOT_COLS = ['super_class', 'flow', 'cell_class', 'cell_sub_class', 'cell_type',
              'hemibrain_type', 'top_nt', 'side', 'nerve']


@dataclass
class Connectome:
    """Edge list + two CSR views of the same signed map, plus the neuron table."""
    n: int
    root_ids: np.ndarray        # (n,) int64, FlyWire root id per neuron index
    pre: np.ndarray             # (m,) int32 presynaptic neuron index per edge
    post: np.ndarray            # (m,) int32 postsynaptic neuron index per edge
    weight: np.ndarray          # (m,) int32 signed synapse count (+ excitatory, - inhibitory)
    neurons: pd.DataFrame       # (n,) rows aligned with the index; ANNOT_COLS (strings, '' if unknown)

    # ---- CSR views (built lazily) -------------------------------------------------
    def csr_by_pre(self):
        """rows = presynaptic neuron; used to push spikes of active neurons outward."""
        if not hasattr(self, '_csr_pre'):
            self._csr_pre = _csr(self.pre, self.post, self.weight, self.n)
        return self._csr_pre

    def csr_by_post(self):
        """rows = postsynaptic neuron; used for dense rate SpMM (x_post = W r_pre)."""
        if not hasattr(self, '_csr_post'):
            self._csr_post = _csr(self.post, self.pre, self.weight, self.n)
        return self._csr_post

    # ---- lookups ------------------------------------------------------------------
    def index_of(self, root_ids) -> np.ndarray:
        """Neuron indices for FlyWire root ids (raises on unknown id)."""
        lut = self._lut()
        idx = np.array([lut[int(r)] for r in root_ids], dtype=np.int64)
        return idx

    def _lut(self):
        if not hasattr(self, '_id2idx'):
            self._id2idx = {int(r): i for i, r in enumerate(self.root_ids)}
        return self._id2idx

    def where(self, **cond) -> np.ndarray:
        """Indices of neurons whose annotation columns equal the given values,
        e.g. where(super_class='descending', side='left')."""
        m = np.ones(self.n, dtype=bool)
        for k, v in cond.items():
            col = self.neurons[k].to_numpy()
            m &= (col == v) if not isinstance(v, (list, tuple, set)) else np.isin(col, list(v))
        return np.flatnonzero(m)

    def summary(self) -> str:
        sc = self.neurons['super_class'].value_counts().to_dict()
        return (f'FlyWire v783: {self.n} neurons, {len(self.pre)} signed connections, '
                f'{int(np.abs(self.weight).sum())} synapses; inhibitory edges '
                f'{(self.weight < 0).mean():.1%}; super_class {sc}')


def _csr(rows, cols, vals, n):
    order = np.argsort(rows, kind='stable')
    r = rows[order]
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, r + 1, 1)
    indptr = np.cumsum(indptr)
    return indptr, cols[order].astype(np.int32), vals[order].astype(np.float32)


def load_connectome(root: str = ROOT_DEFAULT, cache: bool = True) -> Connectome:
    cache_dir = os.path.join(root, 'cache')
    npz = os.path.join(cache_dir, 'edges_783.npz')
    pq = os.path.join(cache_dir, 'neurons_783.parquet')
    if cache and os.path.exists(npz) and os.path.exists(pq):
        z = np.load(npz)
        neurons = pd.read_parquet(pq)
        return Connectome(int(z['n']), z['root_ids'], z['pre'], z['post'], z['weight'], neurons)

    comp = pd.read_csv(os.path.join(root, 'Completeness_783.csv'), index_col=0)
    root_ids = comp.index.to_numpy().astype(np.int64)
    n = len(root_ids)
    con = pd.read_parquet(os.path.join(root, 'Connectivity_783.parquet'))
    pre = con['Presynaptic_Index'].to_numpy().astype(np.int32)
    post = con['Postsynaptic_Index'].to_numpy().astype(np.int32)
    weight = con['Excitatory x Connectivity'].to_numpy().astype(np.int32)
    assert pre.max() < n and post.max() < n, 'edge index outside the completeness table'
    # sanity: the packaged ids must match the completeness index order
    assert (con['Presynaptic_ID'].to_numpy()[:1000] == root_ids[pre[:1000]]).all()

    ann = pd.read_csv(os.path.join(root, 'neuron_annotations.tsv'), sep='\t', low_memory=False)
    ann = ann.drop_duplicates('root_id').set_index('root_id')
    neurons = pd.DataFrame(index=np.arange(n))
    for c in ANNOT_COLS:
        col = ann[c].reindex(root_ids)
        neurons[c] = col.fillna('').astype(str).to_numpy()
    neurons['root_id'] = root_ids

    if cache:
        os.makedirs(cache_dir, exist_ok=True)
        np.savez(npz, n=n, root_ids=root_ids, pre=pre, post=post, weight=weight)
        neurons.to_parquet(pq)
    return Connectome(n, root_ids, pre, post, weight, neurons)
