"""Unit tests for flybrain (CPU, synthetic graphs, seconds). Run: python src/fly_tests.py"""
import os, sys
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain.connectome import Connectome, _csr
from flybrain.dynamics import LifBrain, LifParams, RateBrain


def toy(n=6):
    pre = np.array([0, 0, 1, 2, 3, 4], dtype=np.int32)
    post = np.array([1, 2, 3, 3, 4, 5], dtype=np.int32)
    w = np.array([200, -50, 200, 30, 200, -200], dtype=np.int32)
    neurons = pd.DataFrame({'super_class': ['sensory'] * 2 + ['central'] * 3 + ['motor'], 'cell_type': [''] * n})
    return Connectome(n, np.arange(n, dtype=np.int64) + 10, pre, post, w, neurons)


def test_csr_matches_edges():
    cm = toy()
    ip, cols, vals = cm.csr_by_pre()
    dense = np.zeros((cm.n, cm.n))
    for i in range(cm.n):
        for k in range(ip[i], ip[i + 1]):
            dense[i, cols[k]] += vals[k]
    ref = np.zeros((cm.n, cm.n)); np.add.at(ref, (cm.pre, cm.post), cm.weight)
    assert np.array_equal(dense, ref)
    ip2, cols2, vals2 = cm.csr_by_post()
    dense2 = np.zeros((cm.n, cm.n))
    for j in range(cm.n):
        for k in range(ip2[j], ip2[j + 1]):
            dense2[cols2[k], j] += vals2[k]
    assert np.array_equal(dense2, ref)
    assert list(cm.index_of([10, 15])) == [0, 5]
    assert list(cm.where(super_class='central')) == [2, 3, 4]


def test_lif_chain_and_delay():
    cm = toy(); p = LifParams()
    b = LifBrain(cm, batch=2, params=p, device='cpu')
    b.set_poisson([0], rate_hz=1e9)            # p >= 1: neuron 0 spikes every step
    D = b.D
    first_spike_1 = None
    for t in range(200):
        spk = b.step()
        if spk[0, 1] and first_spike_1 is None:
            first_spike_1 = t
    # neuron 0 spikes at t=0; its 200-synapse (55 mV) input reaches neuron 1 at t=D
    assert first_spike_1 is not None and first_spike_1 >= D, first_spike_1
    assert b.spike_count[0, 0] == 200                # no refractory for Poisson targets
    assert b.spike_count[0, 2] == 0                  # inhibited only: never fires
    assert b.spike_count[0, 5] == 0                  # inhibitory input from 4: never fires
    assert b.spike_count[0, 3] > 0 and b.spike_count[0, 4] > 0
    assert b.v[0, 2] < p.v_0 - 1.0                   # inhibition pushed neuron 2 below rest
    # refractory: neuron 1 cannot fire two steps in a row
    b2 = LifBrain(cm, batch=1, params=p, device='cpu'); b2.set_poisson([0], 1e9)
    spikes1 = [bool(b2.step()[0, 1]) for _ in range(300)]
    gaps = np.diff(np.flatnonzero(spikes1))
    assert gaps.min() >= b2.rfc_steps, gaps.min()


def test_neuron_mask_blocks_propagation():
    cm = toy()
    b = LifBrain(cm, batch=2, device='cpu'); b.set_poisson([0], 1e9)
    mask = np.ones((2, cm.n), dtype=np.float32); mask[1, 0] = 0.0   # being 1: neuron 0 selected out
    b.set_neuron_mask(mask)
    for _ in range(300): b.step()
    assert b.spike_count[0, 1] > 0 and b.spike_count[1, 1] == 0


def test_rate_brain_matches_dense():
    cm = toy()
    rb = RateBrain(cm, batch=3, device='cpu', tau_steps=2.0, scale=0.01)
    W = np.zeros((cm.n, cm.n), dtype=np.float32); np.add.at(W, (cm.post, cm.pre), cm.weight * 0.01)
    x = torch.randn(cm.n, 3); rb.x = x.clone()
    u = torch.randn(cm.n, 3)
    rb.step(u)
    r = torch.relu(x)
    ref = x + 0.5 * (-x + torch.as_tensor(W) @ r + u)
    assert torch.allclose(rb.x, ref, atol=1e-5)


def test_flymap_file_roundtrip():
    import tempfile
    from flybrain.flymap_file import NONE, read_flymap, write_flymap
    cm = toy()
    order = np.argsort(cm.post, kind='stable')
    indptr = np.zeros(cm.n + 1, np.int64); np.add.at(indptr, cm.post + 1, 1); indptr = np.cumsum(indptr)
    type_of = np.array([0, 0, 1, 1, 1, 2], np.uint32)
    in_group_of = np.array([0, 0, NONE, NONE, NONE, NONE], np.uint32)
    out_indptr, out_members = np.array([0, 1], np.uint32), np.array([5], np.uint32)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'toy.bin')
        write_flymap(p, indptr, cm.pre[order], cm.weight[order].astype(np.float32), type_of, in_group_of, out_indptr, out_members,
                     sidecar=dict(k_in=1, n_types=3))
        z = read_flymap(p)
    assert z['n'] == 6 and z['m'] == 6 and z['k_in'] == 1 and z['n_types'] == 3 and z['k_out'] == 1
    assert np.array_equal(z['indptr'], indptr) and np.array_equal(z['indices'], cm.pre[order])
    # row 3 (post=3) has inputs from pre 1 (200) and pre 2 (30)
    r = slice(z['indptr'][3], z['indptr'][4])
    assert sorted(zip(z['indices'][r].tolist(), z['weights'][r].tolist())) == [(1, 200.0), (2, 30.0)]
    assert z['in_group_of'][2] == NONE and z['out_members'].tolist() == [5]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
    print('ALL PASSED')
